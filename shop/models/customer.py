# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _
from django.utils.six import with_metaclass
from jsonfield.fields import JSONField
from . import deferred

SESSION_BASED_USERNAME_PREFIX = '!'  # This will identify a customer by its session key


class CustomerManager(models.Manager):
    BASE64_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + '.@'
    REVERSE_ALPHABET = dict((c, i) for i, c in enumerate(BASE64_ALPHABET))
    BASE36_ALPHABET = string.digits + string.ascii_lowercase

    @classmethod
    def encode_session_key(cls, session_key):
        """
        Session keys have base 36 and length 32. Since the `username` field accepts only up
        to 30 characters, the session key is converted to a base 64 representation, resulting
        in a length of approximately 28.
        """
        return cls._encode(int(session_key, 36), cls.BASE64_ALPHABET)

    @classmethod
    def decode_session_key(cls, compact_session_key):
        """
        Decode a compact session key back to its original length and base.
        """
        compact_session_key = compact_session_key.lstrip(SESSION_BASED_USERNAME_PREFIX)
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

    def create_anonymous_customer(self, compact_session_key):
        user = get_user_model().objects.create(username=compact_session_key)
        user.is_active = False
        user.set_unusable_password()
        customer = self.model(user=user)
        customer.save(using=self._db)
        return customer

    def get_from_request(self, request):
        """
        Return an anonymous Customer object for the current visitor.
        The visitor is determined through the session key.
        """
        assert request.user.is_anonymous(), "Only anonymous Users may be used to fetch session based customers"
        if not request.session.session_key:
            request.session.cycle_key()
            assert request.session.session_key
        compact_session_key = SESSION_BASED_USERNAME_PREFIX + self.encode_session_key(request.session.session_key)
        try:
            return self.get(user__username=compact_session_key)
        except self.model.DoesNotExist:
            return self.create_anonymous_customer(compact_session_key)


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
    salutation = models.CharField(max_length=5, choices=SALUTATION)
    extra = JSONField(default={}, editable=False,
        verbose_name=_("Extra information about this customer"))

    objects = CustomerManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.identifier()

    def identifier(self):
        if self.is_anonymous():
            return '<anonymous>'
        if self.is_guest():
            return self.user.email
        return self.user.username

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

    # There are three possible auth states:
    def is_anonymous(self):
        """
        Return true if the customer isn't associated with valid User account.
        Anonymous customers have accessed the shop, but did not register nor placed an order.
        """
        # TODO: remove 'not self.user.username or '
        return self.user.username.startswith(SESSION_BASED_USERNAME_PREFIX) and not (self.user.email or self.user.is_active)

    def is_guest(self):
        """
        Return true if the customer isn't associated with valid User account, but declared
        himself as a guest, leaving their email address.
        """
        return self.user.username.startswith(SESSION_BASED_USERNAME_PREFIX) and self.user.email and not self.user.is_active

    def is_registered(self):
        """
        Return true if the customer has registered himself.
        """
        return self.user.is_active and not self.user.username.startswith(SESSION_BASED_USERNAME_PREFIX)

    def save(self, *args, **kwargs):
        self.user.save(*args, **kwargs)
        super(BaseCustomer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_registered():
            super(BaseCustomer, self).delete(*args, **kwargs)
        self.user.delete(*args, **kwargs)

CustomerModel = deferred.MaterializedModel(BaseCustomer)


@receiver(user_logged_in)
def handle_customer_login(sender, **kwargs):
    """
    Update request.customer to an authenticated Customer
    """
    kwargs['request'].customer = kwargs['request'].user.customer


@receiver(user_logged_out)
def handle_customer_logout(sender, **kwargs):
    """
    Update request.customer to an anonymous Customer
    """
    # defer assignment to anonymous customer, since the session_key is not yet rotated
    kwargs['request'].customer = SimpleLazyObject(lambda: CustomerModel.objects.get_from_request(kwargs['request']))
