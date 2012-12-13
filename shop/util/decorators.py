"""Decorators for the django-shop application."""
from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shop.util.cart import get_or_create_cart

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

def order_required(url_name='cart'):
    """
    Ensures that an non-complete order exists before carrying out any
    additional functions that rely on one.

    If an order does not exist the browser will be redirected to another page
    supplied in the optional keyword argument `url_name`.

    Usage:
    @order_required
    def some_view(...

    OR:
    @order_required(url_name='cart')
    def some_view(...
    """
    if callable(url_name):
        func = url_name
        decorator = order_required()
        return decorator(func)

    def decorator(func):
        def inner(request, *args, **kwargs):
            order = get_order_from_request(request)
            if order is None or getattr(order, 'status', Order.COMPLETED) >= Order.COMPLETED:
                return HttpResponseRedirect(reverse(url_name))
            return func(request, *args, **kwargs)
        return wraps(func)(inner)
    return decorator

def cart_required(url_name='cart'):
    """
    Ensures that a non-empty cart is present.

    If a cart does not exist the browser will be redirected to another page
    supplied in the optional keyword argument `url_name`.

    Usage:
    @cart_required
    def some_view(...

    OR:
    @cart_required(url_name='cart')
    def some_view(...
    """
    if callable(url_name):
        func = url_name
        decorator = cart_required()
        return decorator(func)

    def decorator(func):
        def inner(request, *args, **kwargs):
            cart = get_or_create_cart(request)
            if cart.total_quantity <= 0:
                return HttpResponseRedirect(reverse(url_name))
            return func(request, *args, **kwargs)
        return wraps(func)(inner)
    return decorator
