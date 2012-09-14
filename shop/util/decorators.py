"""Decorators for the django-shop application."""
from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from shop.util.login_mixin import get_test_func
from shop.util.order import get_order_from_request
from shop.models.ordermodel import Order


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


def order_required(redirect_url, args=[], kwargs={}):
    """
    Ensures that an non-complete order exists before carrying out any
    additional functions that rely on one.

    If an order does not exist the browser will be redirected to another page
    as specified in the argument `redirect_url`.

    `redirect_url` should either be a callable or a reversible named url pattern
    which can be reversed into a url using `django.core.urlresolvers.reverse`.
    The optional keyword arguments `args` and `kwargs` in both cases.


    Usage:
    @order_required(some_function)
    def some_view(...

    OR:
    @order_required('')
    def some_view(...
    """
    def decorator(func):
        def inner(request, *innerargs, **innerkwargs):
            order = get_order_from_request(request)
            if order is None or getattr(order, 'status', Order.COMPLETED) == Order.COMPLETED:
                if callable(redirect_url):
                    redirect = redirect_url(*args, **kwargs)
                else:
                    redirect = reverse(redirect_url, args=args, kwargs=kwargs)
                return HttpResponseRedirect(redirect)
            return func(request, *innerargs, **innerkwargs)
        return wraps(func)(inner)
    return decorator
