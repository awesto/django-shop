# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string
from importlib import import_module
import warnings

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, DEFAULT_DB_ALIAS
from django.db.models.fields import FieldDoesNotExist
from django.dispatch import receiver
from django.utils import timezone
from django.utils.deprecation import CallableBool, CallableFalse, CallableTrue
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _
from django.utils.six import with_metaclass

from shop import deferred
from shop.models.fields import JSONField
from shop.signals import customer_recognized
from shop.models.fields import ChoiceEnum, ChoiceEnumField

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore()


class CustomerState(ChoiceEnum):
    UNRECOGNIZED = 0, _("Unrecognized")
    GUEST = 1, _("Guest")
    REGISTERED = 2, ("Registered")


class CustomerQuerySet(models.QuerySet):
    def _filter_or_exclude(self, negate, *args, **kwargs):
        """
        Emulate filter queries on a Customer using attributes from the User object.
        Example: Customer.objects.filter(last_name__icontains='simpson') will return
        a queryset with customers whose last name contains "simpson".
        """
        opts = self.model._meta
        lookup_kwargs = {}
        for key, lookup in kwargs.items():
            try:
                field_name = key[:key.index('__')]
            except ValueError:
                field_name = key
            if field_name == 'pk':
                field_name = opts.pk.name
            try:
                opts.get_field(field_name)
                if isinstance(lookup, get_user_model()):
                    lookup.pk  # force lazy object to resolve
                lookup_kwargs[key] = lookup
            except FieldDoesNotExist as fdne:
                try:
                    get_user_model()._meta.get_field(field_name)
                    lookup_kwargs['user__' + key] = lookup
                except FieldDoesNotExist:
                    raise fdne
                except Exception as othex:
                    raise othex
        result = super(CustomerQuerySet, self)._filter_or_exclude(negate, *args, **lookup_kwargs)
        return result


class CustomerManager(models.Manager):
    """
    Manager for the Customer database model. This manager can also cope with customers, which have
    an entity in the database but otherwise are considered as anonymous. The username of these
    so called unrecognized customers is a compact version of the session key.
    """
    BASE64_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + '.@'
    REVERSE_ALPHABET = dict((c, i) for i, c in enumerate(BASE64_ALPHABET))
    BASE36_ALPHABET = string.digits + string.ascii_lowercase

    _queryset_class = CustomerQuerySet

    @classmethod
    def encode_session_key(cls, session_key):
        """
        Session keys have base 36 and length 32. Since the field ``username`` accepts only up
        to 30 characters, the session key is converted to a base 64 representation, resulting
        in a length of approximately 28.
        """
        return cls._encode(int(session_key[:32], 36), cls.BASE64_ALPHABET)

    @classmethod
    def decode_session_key(cls, compact_session_key):
        """
        Decode a compact session key back to its original length and base.
        """
        base_length = len(cls.BASE64_ALPHABET)
        n = 0
        for c in compact_session_key:
            n = n * base_length + cls.REVERSE_ALPHABET[c]
        return cls._encode(n, cls.BASE36_ALPHABET).zfill(32)

    @classmethod
    def _encode(cls, n, base_alphabet):
        base_length = len(base_alphabet)
        s = []
        while True:
            n, r = divmod(n, base_length)
            s.append(base_alphabet[r])
            if n == 0:
                break
        return ''.join(reversed(s))

    def get_queryset(self):
        """
        Whenever we fetch from the Customer table, inner join with the User table to reduce the
        number of presumed future queries to the database.
        """
        qs = self._queryset_class(self.model, using=self._db).select_related('user')
        return qs

    def create(self, *args, **kwargs):
        if 'user' in kwargs and kwargs['user'].is_authenticated:
            kwargs.setdefault('recognized', CustomerState.REGISTERED)
        customer = super(CustomerManager, self).create(*args, **kwargs)
        return customer

    def _get_visiting_user(self, session_key):
        """
        Since the Customer has a 1:1 relation with the User object, look for an entity of a
        User object. As its ``username`` (which must be unique), use the given session key.
        """
        username = self.encode_session_key(session_key)
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            user = AnonymousUser()
        return user

    def get_from_request(self, request):
        """
        Return an Customer object for the current User object.
        """
        if request.user.is_anonymous and request.session.session_key:
            # the visitor is determined through the session key
            user = self._get_visiting_user(request.session.session_key)
        else:
            user = request.user
        try:
            if user.customer:
                return user.customer
        except AttributeError:
            pass
        if request.user.is_authenticated:
            customer, created = self.get_or_create(user=user)
            if created:  # `user` has been created by another app than shop
                customer.recognize_as_registered(request)
        else:
            customer = VisitingCustomer()
        return customer

    def get_or_create_from_request(self, request):
        if request.user.is_authenticated:
            user = request.user
            recognized = CustomerState.REGISTERED
        else:
            if not request.session.session_key:
                request.session.cycle_key()
                assert request.session.session_key
            username = self.encode_session_key(request.session.session_key)
            # create or get a previously created inactive intermediate user,
            # which later can declare himself as guest, or register as a valid Django user
            try:
                user = get_user_model().objects.get(username=username)
            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(username)
                user.is_active = False
                user.save()

            recognized = CustomerState.UNRECOGNIZED
        customer, created = self.get_or_create(user=user, recognized=recognized)
        return customer


@python_2_unicode_compatible
class BaseCustomer(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    Base class for shop customers.

    Customer is a profile model that extends
    the django User model if a customer is authenticated. On checkout, a User
    object is created for anonymous customers also (with unusable password).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
    )

    recognized = ChoiceEnumField(
        _("Recognized as"),
        enum_type=CustomerState,
        help_text=_("Designates the state the customer is recognized as."),
    )

    last_access = models.DateTimeField(
        _("Last accessed"),
        default=timezone.now,
    )

    extra = JSONField(
        editable=False,
        verbose_name=_("Extra information about this customer"),
    )

    objects = CustomerManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_username()

    def get_username(self):
        return self.user.get_username()

    def get_full_name(self):
        return self.user.get_full_name()

    @property
    def first_name(self):
        # pending deprecation: warnings.warn("Property first_name is deprecated and will be removed")
        return self.user.first_name

    @first_name.setter
    def first_name(self, value):
        # pending deprecation: warnings.warn("Property first_name is deprecated and will be removed")
        self.user.first_name = value

    @property
    def last_name(self):
        # pending deprecation: warnings.warn("Property last_name is deprecated and will be removed")
        return self.user.last_name

    @last_name.setter
    def last_name(self, value):
        # pending deprecation: warnings.warn("Property last_name is deprecated and will be removed")
        self.user.last_name = value

    @property
    def email(self):
        return self.user.email

    @email.setter
    def email(self, value):
        self.user.email = value

    @property
    def date_joined(self):
        return self.user.date_joined

    @property
    def last_login(self):
        return self.user.last_login

    @property
    def groups(self):
        return self.user.groups

    @property
    def is_anonymous(self):
        return CallableBool(self.recognized in (CustomerState.UNRECOGNIZED, CustomerState.GUEST))

    @property
    def is_authenticated(self):
        return CallableBool(self.recognized is CustomerState.REGISTERED)

    @property
    def is_recognized(self):
        """
        Return True if the customer is associated with a User account.
        Unrecognized customers have accessed the shop, but did not register
        an account nor declared themselves as guests.
        """
        return CallableBool(self.recognized is not CustomerState.UNRECOGNIZED)

    @property
    def is_guest(self):
        """
        Return true if the customer isn't associated with valid User account, but declared
        himself as a guest, leaving their email address.
        """
        return CallableBool(self.recognized is CustomerState.GUEST)

    def recognize_as_guest(self, request=None, commit=True):
        """
        Recognize the current customer as guest customer.
        """
        if self.recognized != CustomerState.GUEST:
            self.recognized = CustomerState.GUEST
            if commit:
                self.save(update_fields=['recognized'])
            customer_recognized.send(sender=self.__class__, customer=self, request=request)

    @property
    def is_registered(self):
        """
        Return true if the customer has registered himself.
        """
        return CallableBool(self.recognized is CustomerState.REGISTERED)

    def recognize_as_registered(self, request=None, commit=True):
        """
        Recognize the current customer as registered customer.
        """
        if self.recognized != CustomerState.REGISTERED:
            self.recognized = CustomerState.REGISTERED
            if commit:
                self.save(update_fields=['recognized'])
            customer_recognized.send(sender=self.__class__, customer=self, request=request)

    @property
    def is_visitor(self):
        """
        Always False for instantiated Customer objects.
        """
        return CallableFalse

    @property
    def is_expired(self):
        """
        Return True if the session of an unrecognized customer expired or is not decodable.
        Registered customers never expire.
        Guest customers only expire, if they failed fulfilling the purchase.
        """
        is_expired = False
        if self.recognized is CustomerState.UNRECOGNIZED:
            try:
                session_key = CustomerManager.decode_session_key(self.user.username)
                is_expired = not SessionStore.exists(session_key)
            except KeyError:
                msg = "Unable to decode username '{}' as session key"
                warnings.warn(msg.format(self.user.username))
                is_expired = True
        return CallableBool(is_expired)

    def get_or_assign_number(self):
        """
        Hook to get or to assign the customers number. It is invoked, every time an Order object
        is created. Using a customer number, which is different from the primary key is useful for
        merchants, wishing to assign sequential numbers only to customers which actually bought
        something. Otherwise the customer number (primary key) is increased whenever a site visitor
        puts something into the cart. If he never proceeds to checkout, that entity expires and may
        be deleted at any time in the future.
        """
        return self.get_number()

    def get_number(self):
        """
        Hook to get the customer's number. Customers haven't purchased anything may return None.
        """
        return str(self.user_id)

    def save(self, **kwargs):
        if 'update_fields' not in kwargs:
            self.user.save(using=kwargs.get('using', DEFAULT_DB_ALIAS))
        super(BaseCustomer, self).save(**kwargs)

    def delete(self, *args, **kwargs):
        if self.user.is_active and self.recognized is CustomerState.UNRECOGNIZED:
            # invalid state of customer, keep the referred User
            super(BaseCustomer, self).delete(*args, **kwargs)
        else:
            # also delete self through cascading
            self.user.delete(*args, **kwargs)

CustomerModel = deferred.MaterializedModel(BaseCustomer)


class VisitingCustomer(object):
    """
    This dummy object is used for customers which just visit the site. Whenever a VisitingCustomer
    adds something to the cart, this object is replaced against a real Customer object.
    """
    user = AnonymousUser()

    def __str__(self):
        return 'Visitor'

    @property
    def email(self):
        return ''

    @email.setter
    def email(self, value):
        pass

    @property
    def is_anonymous(self):
        return CallableTrue

    @property
    def is_authenticated(self):
        return CallableFalse

    @property
    def is_recognized(self):
        return CallableFalse

    @property
    def is_guest(self):
        return CallableFalse

    @property
    def is_registered(self):
        return CallableFalse

    @property
    def is_visitor(self):
        return CallableTrue

    def save(self, **kwargs):
        pass


@receiver(user_logged_in)
def handle_customer_login(sender, **kwargs):
    """
    Update request.customer to an authenticated Customer
    """
    try:
        kwargs['request'].customer = kwargs['user'].customer
    except (AttributeError, ObjectDoesNotExist):
        kwargs['request'].customer = SimpleLazyObject(lambda: CustomerModel.objects.get_from_request(kwargs['request']))


@receiver(user_logged_out)
def handle_customer_logout(sender, **kwargs):
    """
    Update request.customer to a visiting Customer
    """
    # defer assignment to anonymous customer, since the session_key is not yet rotated
    kwargs['request'].customer = SimpleLazyObject(lambda: CustomerModel.objects.get_from_request(kwargs['request']))
