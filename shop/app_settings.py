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
        {symbol}: This is replaced by €, $, £, etc.
        {currency}: This is replaced by EUR, USD, GBP, etc.
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
        This is used by the Django admin and is not visible to the customer.
        """
        return self._setting('SHOP_DECIMAL_PLACES', 2)

    @property
    def CUSTOMER_SERIALIZER(self):
        """
        Depending on the materialized customer model, use this directive to configure the
        customer serializer.

        Defaults to :class:`shop.serializers.defaults.CustomerSerializer`.
        """
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
        """
        Serialize the smallest common denominator of all Product models available in this shop.
        This serialized data then is used for Catalog List Views, Cart List Views and Order List
        Views.

        Defaults to a minimalistic Product serializer.
        """

        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import ProductSerializer

        pss = self._setting('SHOP_PRODUCT_SUMMARY_SERIALIZER')
        if pss:
            ProductSummarySerializer = import_string(pss)
            if not issubclass(ProductSummarySerializer, ProductSerializer):
                raise ImproperlyConfigured(
                    "Serializer class must inherit from 'ProductSerializer'.")
        else:
            class ProductSummarySerializer(ProductSerializer):
                """
                Fallback serializer for the summary of our Product model.
                """
                class Meta(ProductSerializer.Meta):
                    fields = ['id', 'product_name', 'product_url', 'product_model', 'price']
        return ProductSummarySerializer

    @property
    def PRODUCT_SELECT_SERIALIZER(self):
        """
        This serializer is only used by the plugin editors, when selecting a product using a
        drop down menu with auto-completion.

        Defaults to :class:`shop.serializers.defaults.ProductSelectSerializer`.
        """
        from django.utils.module_loading import import_string

        s = self._setting('SHOP_PRODUCT_SELECT_SERIALIZER',
                          'shop.serializers.defaults.ProductSelectSerializer')
        ProductSelectSerializer = import_string(s)
        return ProductSelectSerializer

    @property
    def ORDER_ITEM_SERIALIZER(self):
        """
        Depending on the materialized OrderItem model, use this directive to configure the
        serializer.

        Defaults to :class:`shop.serializers.defaults.OrderItemSerializer`.
        """
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import BaseOrderItemSerializer

        s = self._setting('SHOP_ORDER_ITEM_SERIALIZER',
                          'shop.serializers.defaults.OrderItemSerializer')
        OrderItemSerializer = import_string(s)
        if not issubclass(OrderItemSerializer, BaseOrderItemSerializer):
            raise ImproperlyConfigured(
                "Serializer class must inherit from 'BaseOrderItemSerializer'.")
        return OrderItemSerializer

    @property
    def CART_MODIFIERS(self):
        from django.utils.module_loading import import_string

        cart_modifiers = self._setting('SHOP_CART_MODIFIERS',
                                       ('shop.modifiers.defaults.DefaultCartModifier',))
        return tuple(import_string(mc) for mc in cart_modifiers)

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
        """
        Used to configure the update behavior when changing the quantity of a product, when adding
        it to the cart. For more information refer to the AngularJS docs at:
        https://code.angularjs.org/1.3.7/docs/api/ng/directive/ngModelOptions
        """
        return self._setting('SHOP_ADD2CART_NG_MODEL_OPTIONS',
                             "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")

    @property
    def EDITCART_NG_MODEL_OPTIONS(self):
        """
        Used to configure the update behavior when changing the quantity of a cart item.
        For more information refer to the AngularJS docs at:
        https://code.angularjs.org/1.3.7/docs/api/ng/directive/ngModelOptions
        """
        return self._setting('SHOP_EDITCART_NG_MODEL_OPTIONS',
                             "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")

    @property
    def GUEST_IS_ACTIVE_USER(self):
        """
        If this directive is True, customers which declared themselves as guests, may request
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
