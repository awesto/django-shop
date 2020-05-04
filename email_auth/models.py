"""
Alternative implementation of Django's authentication User model, which allows to authenticate
against the email field in addition to the username fields.
This alternative implementation is activated by setting ``AUTH_USER_MODEL = 'shop.User'`` in
settings.py, otherwise the default Django or another customized implementation will be used.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        try:
            return self.get(username=username)
        except self.model.DoesNotExist:
            return self.get(is_active=True, email=username)


class User(AbstractUser):
    """
    Alternative implementation of Django's User model allowing to authenticate against the email
    field in addition to the username field, which remains the primary unique identifier. The
    email field is only used in addition. For users marked as active, their email address must
    be unique. Guests can reuse their email address as often they want.
    """
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        swappable = 'AUTH_USER_MODEL'

    def get_username(self):
        return self.email

    def __str__(self):
        if self.is_staff or self.is_superuser:
            return self.username
        return self.email or '<anonymous>'

    def get_full_name(self):
        full_name = super(User, self).get_full_name()
        if full_name:
            return full_name
        return self.get_short_name()

    def get_short_name(self):
        short_name = super(User, self).get_short_name()
        if short_name:
            return short_name
        return self.email

    def validate_unique(self, exclude=None):
        """
        Since the email address is used as the primary identifier, we must ensure that it is
        unique. However, since this constraint only applies to active users, it can't be done
        through a field declaration via a database UNIQUE index.

        Inactive users can't login anyway, so we don't need a unique constraint for them.
        """
        super(User, self).validate_unique(exclude)
        if self.email and get_user_model().objects.exclude(id=self.id).filter(is_active=True,
                                                                              email__exact=self.email).exists():
            msg = _("A customer with the e-mail address ‘{email}’ already exists.")
            raise ValidationError({'email': msg.format(email=self.email)})
