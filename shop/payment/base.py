# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns


class PaymentProvider(object):
    """
    Base class for all Payment Service Providers.
    """
    @property
    def namespace(self):
        """
        Use a unique namespace for this payment provider. It is used to build the communication URLs
        exposed to an external payment service provider.
        """
        msg = "The attribute `namespace` must be implemented by the class `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def get_urls(self):
        """
        Return a list of URL patterns for external communication with the payment service provider.
        """
        urlpatterns = patterns('')
        return urlpatterns

    def get_payment_request(self, cart, request):
        """
        Build a JavaScript expression which is evaluated by the success handler on the page
        submitting the purchase command. When redirecting to another page, use:
        ```
        $window.location.href="URL-of-other-page";
        ```
        since this expression is evaluated inside an AngularJS directive.
        """
        return '$window.alert("Please implement method `get_payment_request` in the Python class inheriting from `PaymentProvider`!");'
