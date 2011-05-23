#-*- coding: utf-8 -*-
from django import forms
from shop.models.clientmodel import *
from shop.backends_pool import backends_pool

def get_shipping_backends_choices():
    shipping_backends = backends_pool.get_shipping_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in shipping_backends])

def get_billing_backends_choices():
    billing_backends = backends_pool.get_payment_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in billing_backends])

class BillingShippingForm(forms.Form):
    """
    A form displaying all available payment and shipping methods (the ones defined
    in settings.SHOP_SHIPPING_BACKENDS and settings.SHOP_PAYMENT_BACKENDS)
    """
    shipping_method = forms.ChoiceField(choices=get_shipping_backends_choices())
    payment_method = forms.ChoiceField(choices=get_billing_backends_choices())