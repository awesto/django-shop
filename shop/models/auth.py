# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.core import validators
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


def get_customer(request):
    """
    Always return a Customer object, regardless if the request.user is anonymous or authenticated.
    """
    if isinstance(request.user, AnonymousUser):
        return get_user_model().objects.get_from_request(request)
    else:
        return request.user


class CustomerManager(BaseUserManager):
    def create_user(self, username=None, session_key=None, password=None):
        if username:
            # TODO: use BaseUserManager.normalize_email
            user = self.model(username=username)
            user.is_active = True
            user.set_password(password)
        else:
            user = self.model(session_key=session_key)
            user.is_active = False
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_from_request(self, request):
        """
        Return the user for the current visitor. The visitor is determined through the session key.
        """
        try:
            return self.get(session_key=request.session.session_key)
        except self.model.DoesNotExist:
            return self.create_user(session_key=request.session.session_key)


@python_2_unicode_compatible
class BaseCustomer(AbstractBaseUser, PermissionsMixin):
    """
    Override Django User model with a much longer username and email fields, and a salutation
    field.
    """
    SALUTATION = (('mrs', _("Mrs.")), ('mr', _("Mr.")))
    USERNAME_FIELD = 'username'

    username = models.CharField(max_length=254, unique=True, null=True, blank=True,  # NULL for anonymous customers
        help_text=_("Required. Maximum 254 letters, numbers and the symbols: @ + - _ ."),
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), _("Enter a valid username."), 'invalid')])
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True, editable=False,
        help_text=_("Anonymous customers are identified by their session key"))

    salutation = models.CharField(max_length=5, choices=SALUTATION)
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    email = models.EmailField(_("email Address"), max_length=254)
    is_staff = models.BooleanField(_("Staff status"), default=False,
        help_text=_("Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(_("Active"), default=True,
        help_text=_("Designates whether this user should be treated as active. "
                    "Unselect this instead of deleting accounts."))
    is_registered = models.BooleanField(_("Registered"), default=False,
        help_text=_("Designates whether this customer registered his account or, if he is "
                    "unauthenticated and is is considered as anonymous user."))
    date_joined = models.DateTimeField(_("Date joined"), default=timezone.now)

    class Meta:
        abstract = True

    objects = CustomerManager()

    def identifier(self):
        if self.is_registered:
            return self.username
        elif self.email:
            return self.email
        elif self.username:
            return self.username
        return _("anonymous")

    def get_full_name(self):
        # The user is identified by their email address
        return "{}, {}".format(self.last_name, self.first_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):
        return self.get_short_name()

    def is_anonymous(self):
        """
        Returns True for users without a username.
        """
        return not self.is_registered

    def is_authenticated(self):
        """
        Returns True for users whose username is not None.
        """
        return self.is_registered

    def save(self, *args, **kwargs):
        self.is_registered = self.is_registered or self.is_staff
        super(BaseCustomer, self).save(*args, **kwargs)


# Migrate from auth_user table:
# INSERT INTO stofferia_customer (id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) SELECT id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined from auth_user;
