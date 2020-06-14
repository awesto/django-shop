import warnings

from django.urls import include, path
    
from shop.modifiers.pool import cart_modifiers_pool


urlpatterns = []

# For every payment modifier, load the URLs from the associated `payment_provider`.
for modifier in cart_modifiers_pool.get_payment_modifiers():
    try:
        namespace = modifier.payment_provider.namespace
        path_ = '{}/'.format(namespace)
        urls = modifier.payment_provider.get_urls()
        provider_url = path( path_, include((urls, 'url_payment'), namespace=namespace))
        if provider_url.url_patterns != []:
            urlpatterns.append(provider_url)
    except AttributeError as err:
        warnings.warn(err.message)
