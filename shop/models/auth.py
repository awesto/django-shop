# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.core import validators
from django.db import models
#from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


class CustomerManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError(_("Users must have a valid username."))
        user = self.model(username=self.normalize_email(username))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


@python_2_unicode_compatible
class BaseCustomer(AbstractBaseUser, PermissionsMixin):
    """
    Override Django User model with a much longer username and email fields, and a salutation
    field.
    """
    SALUTATION = (('mrs', _("Mrs.")), ('mr', _("Mr.")))
    USERNAME_FIELD = 'username'

    username = models.CharField(max_length=254, unique=True,
        help_text=_("Required. Maximum 254 letters, numbers and the symbols: @ + - _ ."),
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), _("Enter a valid username."), 'invalid')])

    salutation = models.CharField(max_length=5, choices=SALUTATION)
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    email = models.EmailField(_("email Address"), max_length=254)
    is_staff = models.BooleanField(_("Staff status"), default=False,
        help_text=_("Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(_("Active"), default=True,
        help_text=_("Designates whether this user should be treated as active. "
                    "Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("Date joined"), default=timezone.now)

    class Meta:
        abstract = True

    objects = CustomerManager()

    def get_full_name(self):
        # The user is identified by their email address
        return "{}, {}".format(self.last_name, self.first_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):
        return self.get_short_name()

