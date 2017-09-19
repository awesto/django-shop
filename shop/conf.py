# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class DefaultSettings(object):
    def _setting(self, name, default=None):
        from django.conf import settings
        return getattr(settings, name, default)

    @property
    def SHOP_APP_LABEL(self):
        """
        The name of the project implementing the shop, for instance ``myshop``.

        This is required to assign the abstract shop models to a project. There is no default.
        """
        from django.core.exceptions import ImproperlyConfigured

        result = self._setting('SHOP_APP_LABEL')
        if not result:
            raise ImproperlyConfigured("SHOP_APP_LABEL setting must be set")
        return result

    @property
    def SHOP_DEFAULT_CURRENCY(self):
        """
        The default currency this shop is working with. The default is ``EUR``.

        .. note:: All model- and form input fields can be specified for any other currency, this
                  setting is only used if the supplied currency is missing.
        """
        return self._setting('SHOP_DEFAULT_CURRENCY', 'EUR')

    @property
    def SHOP_VENDOR_EMAIL(self):
        """
        The vendor's email addresses, unless specified through the ``Order`` object.
        """
        try:
            default_email = self._setting('ADMINS')[0][1]
        except IndexError:
            default_email = None
        return self._setting('SHOP_VENDOR_EMAIL', default_email)

    @property
    def SHOP_MONEY_FORMAT(self):
        """
        When rendering an amount of type Money, use this format.

        Possible placeholders are:

        * ``{symbol}``: This is replaced by €, $, £, etc.
        * ``{currency}``: This is replaced by EUR, USD, GBP, etc.
        * ``{amount}``: The localized amount.
        """
        return self._setting('SHOP_MONEY_FORMAT', '{symbol} {amount}')

    @property
    def SHOP_DECIMAL_PLACES(self):
        """
        Number of decimal places for the internal representation of a price.
        This is purely used by the Django admin and is not the number of digits
        visible by the customer.

        Defaults to 2.
        """
        return self._setting('SHOP_DECIMAL_PLACES', 2)

    @property
    def SHOP_CUSTOMER_SERIALIZER(self):
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
    def SHOP_PRODUCT_SUMMARY_SERIALIZER(self):
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
    def SHOP_PRODUCT_SELECT_SERIALIZER(self):
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
    def SHOP_ORDER_ITEM_SERIALIZER(self):
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
    def SHOP_CART_MODIFIERS(self):
        """
        Specifies the list of :ref:`reference/cart-modifiers`. They are are applied on each cart item and the
        cart final sums.

        This list typically starts with ``'shop.modifiers.defaults.DefaultCartModifier'`` as its first entry,
        followed by other cart modifiers.
        """
        from django.utils.module_loading import import_string

        cart_modifiers = self._setting('SHOP_CART_MODIFIERS', ['shop.modifiers.defaults.DefaultCartModifier'])
        return tuple(import_string(mc) for mc in cart_modifiers)

    @property
    def SHOP_VALUE_ADDED_TAX(self):
        """
        Use this convenience settings if you can apply the same tax rate for all products
        and you use one of the default tax modifiers :class:`shop.modifiers.taxes.CartIncludeTaxModifier`
        or :class:`shop.modifiers.taxes.CartExcludedTaxModifier`.

        If your products require individual tax rates or you ship into states with different tax rates,
        then you must provide your own tax modifier.
        """
        from decimal import Decimal
        return self._setting('SHOP_VALUE_ADDED_TAX', Decimal('20'))

    @property
    def SHOP_ORDER_WORKFLOWS(self):
        """
        Specifies a list of :ref:`reference/order-workflows`. Order workflows are applied after
        an order has been created and conduct the vendor through the steps of receiving the payments
        until fulfilling the shipment.
        """
        from django.utils.module_loading import import_string

        order_workflows = self._setting('SHOP_ORDER_WORKFLOWS', [])
        return [import_string(mc) for mc in order_workflows]

    @property
    def SHOP_ADD2CART_NG_MODEL_OPTIONS(self):
        """
        Used to configure the update behavior when changing the quantity of a product, in the product's
        detail view after adding it to the cart. For more information refer to the documentation of the
        NgModelOptions_ directive in the AngularJS reference.

        .. _NgModelOptions: https://code.angularjs.org/1.5.9/docs/api/ng/directive/ngModelOptions
        """
        return self._setting('SHOP_ADD2CART_NG_MODEL_OPTIONS',
                             "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")

    @property
    def SHOP_EDITCART_NG_MODEL_OPTIONS(self):
        """
        Used to configure the update behavior when changing the quantity of a cart item, in the cart's
        edit view.  For more information refer to the documentation of the
        NgModelOptions_ directive in the AngularJS reference.
        """
        return self._setting('SHOP_EDITCART_NG_MODEL_OPTIONS',
                             "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")

    @property
    def SHOP_GUEST_IS_ACTIVE_USER(self):
        """
        If this directive is ``True``, customers which declared themselves as guests, may request
        a password reset, so that they can log into their account at a later time. Then it also
        makes sense to set the ``email`` field in model ``email_auth.User`` as unique.

        The default is ``False``.
        """
        return self._setting('SHOP_GUEST_IS_ACTIVE_USER', False)

    @property
    def SHOP_CACHE_DURATIONS(self):
        """
        In the product's list views, HTML snippets are created for the summary representation of
        each product.

        By default these snippet are cached for one day.
        """
        result = self._setting('SHOP_CACHE_DURATIONS') or {}
        result.setdefault('product_html_snippet', 86400)
        return result

    @property
    def SHOP_DIALOG_FORMS(self):
        """
        Specify a list of dialog forms available in our :class:`shop.views.checkout.CheckoutViewSet`.
        This allows us to use its endpoint ``resolve('shop:checkout-upload')`` in a generic way.

        If Cascade plugins are used for the forms in the checkout view, this list can be empty.
        """
        return self._setting('SHOP_DIALOG_FORMS', [])

    def __getattr__(self, key):
        if not key.startswith('SHOP_'):
            key = 'SHOP_' + key
        return getattr(self, key)

app_settings = DefaultSettings()
