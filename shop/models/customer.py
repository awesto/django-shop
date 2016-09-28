# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string
from importlib import import_module
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, DEFAULT_DB_ALIAS
from django.db.models.fields import FieldDoesNotExist
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _, ugettext_noop
from django.utils.six import with_metaclass
from shop.models.fields import JSONField
from shop import deferred
from .related import ChoiceEnum

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore()


class CustomerState(ChoiceEnum):
    UNRECOGNIZED = 0
    ugettext_noop("CustomerState.Unrecognized")
    GUEST = 1
    ugettext_noop("CustomerState.Guest")
    REGISTERED = 2
    ugettext_noop("CustomerState.Registered")


class CustomerStateField(models.PositiveSmallIntegerField):
    description = _("Customer recognition state")

    def __init__(self, *args, **kwargs):
        kwargs.update(choices=CustomerState.choices())
        kwargs.setdefault('default', CustomerState.UNRECOGNIZED)
        super(CustomerStateField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(CustomerStateField, self).deconstruct()
        del kwargs['choices']
        if kwargs['default'] is CustomerState.UNRECOGNIZED:
            del kwargs['default']
        elif isinstance(kwargs['default'], CustomerState):
            kwargs['default'] = kwargs['default'].value
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        return CustomerState(value)

    def get_prep_value(self, state):
        return state.value

    def to_python(self, state):
        return CustomerState(state)


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
                opts.get_field_by_name(field_name)
                if isinstance(lookup, get_user_model()):
                    lookup.pk  # force lazy object to resolve
                lookup_kwargs[key] = lookup
            except FieldDoesNotExist as fdne:
                try:
                    get_user_model()._meta.get_field_by_name(field_name)
                    lookup_kwargs['user__' + key] = lookup
                except FieldDoesNotExist:
                    raise fdne
                except Exception as othex:
                    raise othex
        result = super(CustomerQuerySet, self)._filter_or_exclude(negate, *args, **lookup_kwargs)
        return result


class CustomerManager(models.Manager):
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
        number of queries to the database.
        """
        qs = self._queryset_class(self.model, using=self._db).select_related('user')
        return qs

    def create(self, *args, **kwargs):
        customer = super(CustomerManager, self).create(*args, **kwargs)
        if 'user' in kwargs and kwargs['user'].is_authenticated():
            customer.recognized = CustomerState.REGISTERED
        return customer

    def _get_visiting_user(self, session_key):
        """
        Since the Customer has a 1:1 relation with the User object, look for an entity for a
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
        if request.user.is_anonymous() and request.session.session_key:
            # the visitor is determined through the session key
            user = self._get_visiting_user(request.session.session_key)
        else:
            user = request.user
        try:
            if user.customer:
                return user.customer
        except AttributeError:
            pass
        if request.user.is_authenticated():
            customer, created = self.get_or_create(user=user)
            if created:  # `user` has been created by another app than shop
                customer.recognized = CustomerState.REGISTERED
                customer.save()
        else:
            customer = VisitingCustomer()
        return customer

    def get_or_create_from_request(self, request):
        if request.user.is_authenticated():
            user = request.user
            recognized = CustomerState.REGISTERED
        else:
            if not request.session.session_key:
                request.session.cycle_key()
                assert request.session.session_key
            username = self.encode_session_key(request.session.session_key)
            # create an inactive intermediate user, which later can declare himself as
            # guest, or register as a valid Django user
            user = get_user_model().objects.create_user(username)
            user.is_active = False
            user.save()
            recognized = CustomerState.UNRECOGNIZED
        customer = self.get_or_create(user=user)[0]
        customer.recognized = recognized
        return customer


@python_2_unicode_compatible
class BaseCustomer(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    Base class for shop customers.

    Customer is a profile model that extends
    the django User model if a customer is authenticated. On checkout, a User
    object is created for anonymous customers also (with unusable password).
    """
    SALUTATION = (('mrs', _("Mrs.")), ('mr', _("Mr.")), ('na', _("(n/a)")))

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    recognized = CustomerStateField(_("Recognized as"), default=CustomerState.UNRECOGNIZED,
                                    help_text=_("Designates the state the customer is recognized as."))
    salutation = models.CharField(_("Salutation"), max_length=5, choices=SALUTATION)
    last_access = models.DateTimeField(_("Last accessed"), default=timezone.now)
    extra = JSONField(editable=False, verbose_name=_("Extra information about this customer"))

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
        return self.user.first_name

    @first_name.setter
    def first_name(self, value):
        self.user.first_name = value

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value):
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

    def is_anonymous(self):
        return self.recognized in (CustomerState.UNRECOGNIZED, CustomerState.GUEST)

    def is_authenticated(self):
        return self.recognized is CustomerState.REGISTERED

    def is_recognized(self):
        """
        Return True if the customer is associated with a User account.
        Unrecognized customers have accessed the shop, but did not register
        an account nor declared themselves as guests.
        """
        return self.recognized is not CustomerState.UNRECOGNIZED

    def is_guest(self):
        """
        Return true if the customer isn't associated with valid User account, but declared
        himself as a guest, leaving their email address.
        """
        return self.recognized is CustomerState.GUEST

    def recognize_as_guest(self):
        """
        Recognize the current customer as guest customer.
        """
        self.recognized = CustomerState.GUEST

    def is_registered(self):
        """
        Return true if the customer has registered himself.
        """
        return self.recognized is CustomerState.REGISTERED

    def recognize_as_registered(self):
        """
        Recognize the current customer as registered customer.
        """
        self.recognized = CustomerState.REGISTERED

    def unrecognize(self):
        """
        Unrecognize the current customer.
        """
        self.recognized = CustomerState.UNRECOGNIZED

    def is_visitor(self):
        """
        Always False for instantiated Customer objects.
        """
        return False

    def is_expired(self):
        """
        Return true if the session of an unrecognized customer expired.
        Registered customers never expire.
        Guest customers only expire, if they failed fulfilling the purchase (currently not implemented).
        """
        if self.recognized is CustomerState.UNRECOGNIZED:
            session_key = CustomerManager.decode_session_key(self.user.username)
            return not SessionStore.exists(session_key)
        return False

    def get_or_assign_number(self):
        """
        Hook to get or to assign the customers number. It is invoked, every time an Order object
        is created. Using a customer number, which is different from the primary key is useful for
        merchants, wishing to assign sequential numbers only to customers which actually bought
        something. Otherwise the customer number (primary key) is increased whenever a customer
        puts something into the cart.
        """
        return self.get_number()

    def get_number(self):
        """
        Hook to get the customers number. Customers haven't purchased anything may return None.
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

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

    def is_recognized(self):
        return False

    def is_guest(self):
        return False

    def is_registered(self):
        return False

    def is_visitor(self):
        return True

    def save(self, **kwargs):
        pass


@receiver(user_logged_in)
def handle_customer_login(sender, **kwargs):
    """
    Update request.customer to an authenticated Customer
    """
    try:
        kwargs['request'].customer = kwargs['request'].user.customer
    except (AttributeError, ObjectDoesNotExist):
        kwargs['request'].customer = SimpleLazyObject(lambda: CustomerModel.objects.get_from_request(kwargs['request']))


@receiver(user_logged_out)
def handle_customer_logout(sender, **kwargs):
    """
    Update request.customer to a visiting Customer
    """
    # defer assignment to anonymous customer, since the session_key is not yet rotated
    kwargs['request'].customer = SimpleLazyObject(lambda: CustomerModel.objects.get_from_request(kwargs['request']))
