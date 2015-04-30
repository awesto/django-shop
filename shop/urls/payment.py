# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, include
from shop.modifiers.pool import cart_modifiers_pool


urlpatterns = patterns('')

# For every payment modifier, load all the URLs the associate `payment_service` provides.
for modifier in cart_modifiers_pool.get_payment_modifiers():
    try:
        namespace = modifier.payment_service.namespace
        regexp = r'^{}/'.format(namespace)
        urls = modifier.payment_service.get_urls()
        pattern = patterns('',
            (regexp, include(urls, namespace=namespace))
        )
        urlpatterns = pattern + urlpatterns
    except AttributeError:
        pass
