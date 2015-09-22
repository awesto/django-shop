# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Alternative implementation of Django's authentication model.
"""
import re
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError("The given email address must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True,
            is_superuser=is_superuser, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


@python_2_unicode_compatible
class User(AbstractBaseUser, PermissionsMixin):
    """
    Replace the Django User model, so that the email address is used instead of the username.
    To activate, import this User model into the models.py of your your application and in
    settings.py, point ``AUTH_USER_MODEL`` onto this imported User model.
    """
    USERNAME_REGEX = re.compile('^[\w.@+-]+$')

    email = models.EmailField(_("Email address"), null=True, default=None, unique=True, max_length=254)

    # some authentication require the username, regardless of the USERNAME_FIELD setting below
    username = models.CharField(_("Username"), max_length=30, unique=True,
        help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"),
        validators=[(validators.RegexValidator(USERNAME_REGEX), _("Enter a valid username."), 'invalid')])

    # copied from django.contrib.auth.models.AbstractUser
    first_name = models.CharField(_("First name"), max_length=30, blank=True)
    last_name = models.CharField(_("Last name"), max_length=30, blank=True)
    is_staff = models.BooleanField(_("staff status"), default=False,
        help_text=_("Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this user should be treated as active."
                    "Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        app_label = 'shop'
        db_table = 'auth_user'
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return self.get_username()

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        full_name = full_name.strip()
        if full_name:
            return full_name
        return self.get_short_name()

    def get_short_name(self):
        if self.USERNAME_REGEX.match(self.username):
            return self.username
        return self.email

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])
