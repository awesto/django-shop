"""Decorators for the django-shop application."""
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

from shop.util.login_mixin import get_test_func


def on_method(function_decorator):
    """
    Enables decorators for functions of classes (for example class based
    views).

    Credits go to: http://www.toddreed.name/content/django-view-class/
    """
    def decorate_method(unbound_method):
        def method_proxy(self, *args, **kwargs):
            def f(*a, **kw):
                return unbound_method(self, *a, **kw)
            return function_decorator(f)(*args, **kwargs)
        return method_proxy
    return decorate_method


def shop_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME,
                        login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.

    Takes the `SHOP_FORCE_LOGIN` setting into consideration.
    """
    actual_decorator = user_passes_test(
        get_test_func(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
