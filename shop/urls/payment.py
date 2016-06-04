# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django.conf.urls import include, url
from shop.modifiers.pool import cart_modifiers_pool


urlpatterns = []

# For every payment modifier, load the URLs from the associated `payment_provider`.
for modifier in cart_modifiers_pool.get_payment_modifiers():
    try:
        namespace = modifier.payment_provider.namespace
        regexp = r'^{}/'.format(namespace)
        urls = modifier.payment_provider.get_urls()
        urlpatterns.append(url(regexp, include(urls, namespace=namespace)))
    except AttributeError as err:
        warnings.warn(err.message)
