# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django.conf.urls import patterns
from cms.models import Page


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
        return NotImplemented

    def get_urls(self):
        """
        Return a list of URL patterns for external communication with the payment service provider.
        """
        urlpatterns = patterns('')
        return urlpatterns

    def get_payment_request(self, cart, request):
        """
        Build a JavaScript expression which is evaluated by the success handler on the page
        summiting the purchase command. When redirecting to another page, use:
        ```
        $window.location.href="URL-of-other-page";
        ```
        since this expression is evaluated inside an AngularJS directive.
        """
        return '$window.alert("Please implement method `get_payment_request` in the Python class inheriting from `PaymentProvider`!");'

    def get_purchase_confirmation_url(self):
        """
        Return the URL of the CMS page confirming the purchase. This page normally says something
        such as "Thank you for buying here".
        """
        try:
            url = Page.objects.public().get(reverse_id='purchase-confirmation').get_absolute_url()
        except Page.DoesNotExist:
            warnings.warn("Please add a page with an id `purchase-confirmation` to the CMS.")
            url = '/page_purchase-confirmation_not-found-in-cms'
        return url
