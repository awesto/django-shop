"""
A mixin class that provides view securing functionality to class based views
similar to the @login_required() decorator.
"""
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect


class LoginMixin(object):
    """
    Mixin for securing a class.

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
        return get_test_func(getattr(self, 'test_func', None))

    def get_login_url(self):
        """Returns the login URL."""
        return getattr(self, 'login_url', None)

    def get_redirect_field_name(self):
        """Returns the redirect_field_name."""
        return getattr(self, 'redirect_field_name', None)

    def dispatch(self, request, *args, **kwargs):
        test_kwargs = {}
        login_url = self.get_login_url()
        if login_url:
            test_kwargs['login_url'] = login_url
        redirect_field_name = self.get_redirect_field_name()
        if redirect_field_name:
            test_kwargs['redirect_field_name'] = redirect_field_name
        return user_passes_test(
            self.get_test_func(),
            **test_kwargs)(super(LoginMixin, self).dispatch)(
                request, *args, **kwargs)


def get_test_func(test_func=None):
    """
    Returns the test function to be used for authentication and takes the
    setting `SHOP_FORCE_LOGIN` into consideration.

    :param test_func: Optional. You can provide your own test function for
      authentication. This should be a lambda expression.
    """
    if getattr(settings, 'SHOP_FORCE_LOGIN', False):
        if test_func:
            return test_func
        return lambda u: u.is_authenticated()
    else:
        return lambda u: True
