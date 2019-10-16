# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION < (2, 0):
    from django.conf.urls import include, url
else:    
    from django.urls import include, path
    
from shop.modifiers.pool import cart_modifiers_pool

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION < (2, 0):
    from django.conf.urls import include, url
else:    
    from django.urls import include, path
    
from shop.modifiers.pool import cart_modifiers_pool

urlpatterns = []

for modifier in cart_modifiers_pool.get_payment_modifiers():
    try:
        if DJANGO_VERSION < (2, 0):
            namespace = modifier.payment_provider.namespace
        if DJANGO_VERSION < (2, 0):
            regexp = r'^{}/'.format(namespace)
            urls = modifier.payment_provider.get_urls()
            provider_url = url(regexp, include(urls, namespace=namespace))
            if provider_url.describe() not in [u.describe() for u in urlpatterns]:
                urlpatterns.append(provider_url)
        else:
            namespace = modifier.payment_provider.namespace
            path_ = '{}/'.format(namespace)
            urls = modifier.payment_provider.get_urls()
            provider_url = path( path_, include((urls, 'url_payment'), namespace=namespace))
            if provider_url.url_patterns != []:
                urlpatterns.append(provider_url)
    except AttributeError as err:
        warnings.warn(err.message)
