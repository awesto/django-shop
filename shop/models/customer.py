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
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _
from django.utils.six import with_metaclass
from jsonfield.fields import JSONField
from . import deferred

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore()


class CustomerManager(models.Manager):
    BASE64_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + '.@'
    REVERSE_ALPHABET = dict((c, i) for i, c in enumerate(BASE64_ALPHABET))
    BASE36_ALPHABET = string.digits + string.ascii_lowercase

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
        compact_session_key = compact_session_key
        base_length = len(cls.BASE64_ALPHABET)
        n = 0
        for c in compact_session_key:
            n = n * base_length + cls.REVERSE_ALPHABET[c]
        return cls._encode(n, cls.BASE36_ALPHABET)

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
        qs = super(CustomerManager, self).get_queryset().select_related('user')
        return qs

    def get_unregistered_user(self, session_key):
        """
        Since the Customer has a 1:1 relation with the User object, get an unregistered entity in
        models User. As its ``username`` (which must be unique), use a compressed representation
        of the given session key.
        """
        username = self.encode_session_key(session_key)
        try:
            user = get_user_model().objects.get_or_create(username=username)
        except get_user_model().DoesNotExists:
            user.is_active = False
            user.set_unusable_password()
        return user

    def get_from_request(self, request):
        """
        Return an Customer object for the current visitor.
        """
        if isinstance(request.user, AnonymousUser):
            # the visitor is determined through the session key
            if not request.session.session_key:
                request.session.cycle_key()
                assert request.session.session_key
            user = self.get_or_create_anonymous_user(request.session.session_key)
        else:
            user = request.user
        try:
            if user.customer:
                return user.customer
        finally:
            return VisitingCustomer
            #customer = self.get_or_create(user=user)[0]
            #return customer


@python_2_unicode_compatible
class BaseCustomer(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    Base class for shop customers.

    Customer is a profile model that extends
    the django User model if a customer is authenticated. On checkout, a User
    object is created for anonymous customers also (with unusable password).
    """
    SALUTATION = (('mrs', _("Mrs.")), ('mr', _("Mr.")), ('na', _("(n/a)")))
    UNRECOGNIZED = 0
    GUEST = 1
    REGISTERED = 2
    CUSTOMER_STATES = ((UNRECOGNIZED, _("Unrecognized")), (GUEST, _("Guest")), (REGISTERED, _("Registered")))

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    recognized = models.PositiveSmallIntegerField(_("Recognized as"), choices=CUSTOMER_STATES,
        help_text=_("Designates the state the customer is recognized as."), default=0)
    salutation = models.CharField(_("Salutation"), max_length=5, choices=SALUTATION)
    last_access = models.DateTimeField(_("Last accessed"), default=timezone.now)
    extra = JSONField(default={}, editable=False,
        verbose_name=_("Extra information about this customer"))

    objects = CustomerManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_username()

    def get_username(self):
        return self.user.get_username()

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

    def is_anonymous(self):
        return self.recognized in (self.UNRECOGNIZED, self.GUEST)

    def is_authenticated(self):
        return self.recognized == self.REGISTERED

    def is_recognized(self):
        """
        Return True if the customer is associated with a User account.
        Non recognized customers have accessed the shop, but did not register
        an account nor declared themselves as guests.
        """
        return self.recognized != self.UNRECOGNIZED

    def is_guest(self):
        """
        Return true if the customer isn't associated with valid User account, but declared
        himself as a guest, leaving their email address.
        """
        return self.recognized == self.GUEST

    def is_registered(self):
        """
        Return true if the customer has registered himself.
        """
        return self.recognized == self.REGISTERED

    def is_visitor(self):
        """
        Always False for instantiated Customer objects.
        """
        return False

    def is_expired(self):
        """
        Return true if the session of an unregistered customer expired.
        """
        if self.recognized in (self.GUEST, self.REGISTERED):
            return False
        session_key = CustomerManager.decode_session_key(self.user.username)
        return not SessionStore.exists(session_key)

    def get_number(self):
        """
        Hook to get or to assign the customers number. It will be invoked, every time an Order
        object is created. If you prefer to use a customer number which differs from the primary
        key, then override this method.
        """
        return self.user_id

    def save(self, **kwargs):
        if 'update_fields' not in kwargs:
            self.user.save(using=kwargs.get('using', DEFAULT_DB_ALIAS))
        super(BaseCustomer, self).save(**kwargs)

    def delete(self, *args, **kwargs):
        if self.user.is_active and not self.recognized:
            # invalid state of customer
            super(BaseCustomer, self).delete(*args, **kwargs)
        self.user.delete(*args, **kwargs)

CustomerModel = deferred.MaterializedModel(BaseCustomer)


class VisitingCustomer(object):
    """
    This dummy object is used for customers which just visit the site. Whenever a VisitingCustomer
    adds something to the cart, this object is replaced against a real Customer object.
    """
    user = AnonymousUser

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
    Update request.customer to an anonymous Customer
    """
    # defer assignment to anonymous customer, since the session_key is not yet rotated
    kwargs['request'].customer = SimpleLazyObject(lambda: CustomerModel.objects.get_from_request(kwargs['request']))
