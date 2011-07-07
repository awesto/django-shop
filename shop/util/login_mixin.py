"""
A mixin class that provides view securing functionality to class based views
similar to the @login_required() decorator.
"""
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class LoginMixin(object):
    """Mixin for securing a class.

    Taken from here:
    https://groups.google.com/d/msg/django-users/g2E_6ZYN_R0/tnB9b262lcAJ
    """

    def do_logout(self, request):
        """Logs the user out if necessary."""
        logout(request)
        return HttpResponseRedirect(self.get_login_url())

    def get_test_func(self):
        """
        Returns the function that is being used to test if a user is
        authenticated.
        """
        if getattr(settings, 'SHOP_FORCE_LOGIN', False):
            return getattr(self, 'test_func', lambda u: u.is_authenticated())
        else:
            return lambda x: True

    def get_login_url(self):
        """Returns the login URL."""
        return getattr(self, 'login_url', None)

    def get_redirect_field_name(self):
        """Returns the redirect_field_name."""
        return getattr(self, 'redirect_field_name', None)

    def dispatch(self, request, *args, **kwargs):
        return user_passes_test(
            self.get_test_func(),
            login_url=self.get_login_url(),
            redirect_field_name=self.get_redirect_field_name()
        )(super(LoginMixin, self).dispatch)(request, *args, **kwargs)
