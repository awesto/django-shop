# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.conf import app_settings
from shop.models.customer import CustomerModel


def customer(request):
    """
    Add the customer to the RequestContext
    """
    msg = "The request object does not contain a customer. Edit your MIDDLEWARE_CLASSES setting to insert 'shop.middlerware.CustomerMiddleware'."
    assert hasattr(request, 'customer'), msg

    context = {
        'customer': request.customer,
        'site_header': app_settings.APP_LABEL.capitalize(),
    }
    if request.user.is_staff:
        try:
            context.update(customer=CustomerModel.objects.get(pk=request.session['emulate_user_id']))
        except (CustomerModel.DoesNotExist, KeyError, AttributeError):
            pass
    return context


def shop_settings(request):
    """
    Add configuration settings to the context to customize the shop's settings in templates
    """
    from rest_auth.app_settings import LoginSerializer
    return {
        'EDITCART_NG_MODEL_OPTIONS': app_settings.EDITCART_NG_MODEL_OPTIONS,
        'ADD2CART_NG_MODEL_OPTIONS': app_settings.ADD2CART_NG_MODEL_OPTIONS,
        'ALLOW_SHORT_SESSIONS': 'stay_logged_in' in LoginSerializer().fields,
        'LINK_TO_EMPTY_CART': app_settings.LINK_TO_EMPTY_CART,
    }
