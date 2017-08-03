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


def ng_model_options(request):
    """
    Add ng-model-options to the context, since these settings must be configurable
    """
    return {
        'EDITCART_NG_MODEL_OPTIONS': app_settings.EDITCART_NG_MODEL_OPTIONS,
        'ADD2CART_NG_MODEL_OPTIONS': app_settings.ADD2CART_NG_MODEL_OPTIONS,
    }
