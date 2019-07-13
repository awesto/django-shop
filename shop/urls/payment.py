# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings

from django.urls import include, path, re_path
from shop.modifiers.pool import cart_modifiers_pool


urlpatterns = []

for modifier in cart_modifiers_pool.get_payment_modifiers():
    try:
        namespace = modifier.payment_provider.namespace
       # regexp = r'^{}/'.format(namespace)
        path_ = '{}/'.format(namespace)
        urls = modifier.payment_provider.get_urls()
        provider_url = path( path_, include((urls, 'url_payment'), namespace=namespace))
        if provider_url.url_patterns != []:
            urlpatterns.append(provider_url)
    except AttributeError as err:
        warnings.warn(err.message)
        
