# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django.urls import include, path, re_path
#from django.conf.urls import include, url
from shop.modifiers.pool import cart_modifiers_pool
 
urlpatterns = []

# For every payment modifier, load the URLs from the associated `payment_provider`.
for modifier in cart_modifiers_pool.get_payment_modifiers():
    try:
        namespace = modifier.payment_provider.namespace
       # regexp = r'^{}/'.format(namespace)
        path_ = '{}/'.format(namespace)
        urls = modifier.payment_provider.get_urls()
        if len(namespace) == 0 :
            provider_url = path( path_, include(urls, namespace=namespace))
            if provider_url.describe() not in [u.describe() for u in urlpatterns]:
                pass
                #urlpatterns.append(provider_url)
    except AttributeError as err:
        warnings.warn(err.message)
