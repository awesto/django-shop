# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class AppSettings(object):

    def _setting(self, name, default=None):
        from django.conf import settings
        return getattr(settings, name, default)

    @property
    def APP_LABEL(self):
        from django.core.exceptions import ImproperlyConfigured

        result = self._setting('SHOP_APP_LABEL')
        if not result:
            raise ImproperlyConfigured("SHOP_APP_LABEL setting must be set")
        return result

    @property
    def DEFAULT_CURRENCY(self):
        return self._setting('SHOP_DEFAULT_CURRENCY', 'EUR')

    @property
    def MONEY_FORMAT(self):
        """
        When rendering an amount of type Money, use this format.
        Possible placeholders are:
        {symbol}: This can be €, $, £, etc.
        {currency}: This can be EUR, USD, GBP, etc.
        {amount}: The localized amount.
        """
        return self._setting('SHOP_MONEY_FORMAT', '{symbol} {amount}')

    @property
    def USE_TZ(self):
        return True

    @property
    def DECIMAL_PLACES(self):
        """
        Number of decimal places for the internal representation of a price.
        Not visible to the customer.
        """
        return self._setting('SHOP_DECIMAL_PLACES', 2)

    @property
    def CUSTOMER_SERIALIZER(self):
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import BaseCustomerSerializer

        s = self._setting('SHOP_CUSTOMER_SERIALIZER', 'shop.serializers.defaults.CustomerSerializer')
        CustomerSerializer = import_string(s)
        if not issubclass(CustomerSerializer, BaseCustomerSerializer):
            raise ImproperlyConfigured(
                "Serializer class must inherit from 'BaseCustomerSerializer'.")
        return CustomerSerializer

    @property
    def PRODUCT_SUMMARY_SERIALIZER(self):
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import BaseProductSummarySerializer

        s = self._setting('SHOP_PRODUCT_SUMMARY_SERIALIZER')
        if not s:
            raise ImproperlyConfigured("SHOP_PRODUCT_SUMMARY_SERIALIZER setting must be set")
        ProductSummarySerializer = import_string(s)
        if not issubclass(ProductSummarySerializer, BaseProductSummarySerializer):
            raise ImproperlyConfigured(
                "Serializer class must inherit from 'BaseProductSummarySerializer'.")
        return ProductSummarySerializer

    @property
    def ORDER_ITEM_SERIALIZER(self):
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import BaseOrderItemSerializer

        s = self._setting('SHOP_ORDER_ITEM_SERIALIZER', 'shop.serializers.defaults.OrderItemSerializer')
        OrderItemSerializer = import_string(s)
        if not issubclass(OrderItemSerializer, BaseOrderItemSerializer):
            raise ImproperlyConfigured(
                "Serializer class must inherit from 'BaseOrderItemSerializer'.")
        return OrderItemSerializer

    @property
    def CART_MODIFIERS(self):
        from django.utils.module_loading import import_string
        return tuple(
            import_string(mc)
            for mc in self._setting('SHOP_CART_MODIFIERS', ('shop.modifiers.defaults.DefaultCartModifier',))
        )

    @property
    def VALUE_ADDED_TAX(self):
        from decimal import Decimal
        return self._setting('SHOP_VALUE_ADDED_TAX', Decimal('20'))

    @property
    def ORDER_WORKFLOWS(self):
        from django.utils.module_loading import import_string
        return tuple(
            import_string(mc)
            for mc in self._setting('SHOP_ORDER_WORKFLOWS', ())
        )

    @property
    def ADD2CART_NG_MODEL_OPTIONS(self):
        return self._setting('SHOP_ADD2CART_NG_MODEL_OPTIONS', "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")

    @property
    def EDITCART_NG_MODEL_OPTIONS(self):
        """
        Use ``SHOP_EDITCART_NG_MODEL_OPTIONS`` and ``SHOP_ADD2CART_NG_MODEL_OPTIONS`` to configure the
        update behavior when changing the quantity of a cart item. For more information refer to the
        AngularJS docs: https://code.angularjs.org/1.3.7/docs/api/ng/directive/ngModelOptions
        """
        return self._setting('SHOP_EDITCART_NG_MODEL_OPTIONS', "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")

    @property
    def GUEST_IS_ACTIVE_USER(self):
        """
        If ``SHOP_GUEST_IS_ACTIVE_USER`` is True, Customers which declared themselves as guests, may request
        a password reset, so that they can log into their account at a later time. The default is False.
        """
        return self._setting('SHOP_GUEST_IS_ACTIVE_USER', False)

    @property
    def CACHE_DURATIONS(self):
        result = self._setting('SHOP_CACHE_DURATIONS') or {}
        result.setdefault('product_html_snippet', 86400)
        return result


# Change the export value of the module, to allow importing with `from shop import app_settings`
# For more details, see http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa
app_settings = AppSettings()
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
