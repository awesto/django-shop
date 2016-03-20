# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import with_metaclass
from django.conf.urls import patterns


class ShippingProviderRegistry(type):
    pool = {}

    def __new__(cls, name, bases, attrs):
        new_class = super(ShippingProviderRegistry, cls).__new__(cls, name, bases, attrs)
        try:
            cls.pool[str(new_class().namespace)] = new_class
        except NotImplementedError:
            pass
        return new_class


class ShippingProvider(with_metaclass(ShippingProviderRegistry)):
    """
    Base class for all Shipping Providers.
    """
    @property
    def namespace(self):
        """
        Use a unique namespace for this shipping provider. It is used to keep state over how each
        item was shipped to the customer.
        """
        msg = "The attribute `namespace` must be implemented by the class `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def get_urls(self):
        """
        Return a list of URL patterns for external communication with the shipping service provider.
        """
        urlpatterns = patterns('')
        return urlpatterns
