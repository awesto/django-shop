#-*- coding: utf-8 -*-
from django.conf import settings
from shop.payment.api import PaymentAPI
from shop.shipping.api import ShippingAPI
from shop.util.loader import load_class


class BackendsPool(object):
    """
    A pool for backends.
    It handles loading backend modules (both shipping and payment backends),
    and keeping a cached copy of the classes in-memory (so that the backends
    aren't loaded from file every time one requests them)
    """

    SHIPPING = 'SHOP_SHIPPING_BACKENDS'
    PAYMENT = 'SHOP_PAYMENT_BACKENDS'

    PAYMENT_SHOP_INTERFACE = PaymentAPI()
    SHIPPING_SHOP_INTERFACE = ShippingAPI()

    def __init__(self, use_cache=True):
        """
        The use_cache parameter is mostly used for testing, since setting it
        to false will trigger reloading from disk
        """
        self._payment_backends_list = []
        self._shippment_backends_list = []
        self.use_cache = use_cache

    def get_payment_backends_list(self):
        """
        Returns the list of payment backends, as instances, from the list of
        backends defined in settings.SHOP_PAYMENT_BACKENDS
        """
        if self._payment_backends_list and self.use_cache:
            return self._payment_backends_list
        else:
            self._payment_backends_list = self._load_backends_list(
                self.PAYMENT, self.PAYMENT_SHOP_INTERFACE)
            return self._payment_backends_list

    def get_shipping_backends_list(self):
        """
        Returns the list of shipping backends, as instances, from the list of
        backends defined in settings.SHOP_SHIPPING_BACKENDS
        """
        if self._shippment_backends_list and self.use_cache:
            return self._shippment_backends_list
        else:
            self._shippment_backends_list = self._load_backends_list(
                self.SHIPPING, self.SHIPPING_SHOP_INTERFACE)
            return self._shippment_backends_list

    def _check_backend_for_validity(self, backend_instance):
        """
        This enforces having a valid name and url namespace defined.
        Backends, both shipping and payment are namespaced in respectively
        /pay/ and /ship/ URL spaces, so as to avoid name clashes.

        "Namespaces are one honking great idea -- let's do more of those!"
        """
        backend_name = getattr(backend_instance, 'backend_name', "")
        if not backend_name:
            d_tuple = (str(backend_instance), str(type(backend_instance)))
            raise NotImplementedError(
                'One of your backends ("%s" of type "%s") lacks a name, please'
                ' define one.' % d_tuple)

        url_namespace = getattr(backend_instance, 'url_namespace', "")
        if not url_namespace:
            raise NotImplementedError(
                'Please set a namespace for backend "%s"' %
                    backend_instance.backend_name)

    def _load_backends_list(self, setting_name, shop_object):
        """ This actually loads the backends from disk"""
        result = []
        if not getattr(settings, setting_name, None):
            return result

        for backend_path in getattr(settings, setting_name, None):
            # The load_class function takes care of the classloading. It
            # returns a CLASS, not an INSTANCE!
            mod_class = load_class(backend_path, setting_name)

            # Seems like it is a real, valid class - let's instanciate it!
            # This is where the backends receive their self.shop reference!
            mod_instance = mod_class(shop=shop_object)

            self._check_backend_for_validity(mod_instance)

            # The backend seems valid (nothing raised), let's add it to the
            # return list.
            result.append(mod_instance)

        return result


backends_pool = BackendsPool()
