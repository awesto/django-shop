class DefaultSettings:
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
        * ``{currency}``: This is replaced by Euro, US Dollar, Pound Sterling, etc.
        * ``{code}``: This is replaced by EUR, USD, GBP, etc.
        * ``{amount}``: The localized amount.
        * ``{minus}``: Only for negative amounts, where to put the ``-`` sign.

        For further information about formatting currency amounts, please refer to
        https://docs.microsoft.com/en-us/globalization/locale/currency-formatting
        """
        return self._setting('SHOP_MONEY_FORMAT', '{minus}{symbol} {amount}')

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

        Defaults to :class:`shop.serializers.defaults.customer.CustomerSerializer`.
        """
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import BaseCustomerSerializer

        s = self._setting('SHOP_CUSTOMER_SERIALIZER', 'shop.serializers.defaults.customer.CustomerSerializer')
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

        Defaults to :class:`shop.serializers.defaults.product_summary.ProductSummarySerializer`.
        """
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.module_loading import import_string
        from shop.serializers.bases import ProductSerializer

        s = self._setting('SHOP_PRODUCT_SUMMARY_SERIALIZER',
                          'shop.serializers.defaults.product_summary.ProductSummarySerializer')
        ProductSummarySerializer = import_string(s)
        if not issubclass(ProductSummarySerializer, ProductSerializer):
            msg = "class {} specified in SHOP_PRODUCT_SUMMARY_SERIALIZER must inherit from 'ProductSerializer'."
            raise ImproperlyConfigured(msg.format(s))
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
                          'shop.serializers.defaults.product_select.ProductSelectSerializer')
        ProductSelectSerializer = import_string(s)
        return ProductSelectSerializer

    @property
    def SHOP_MAX_PURCHASE_QUANTITY(self):
        """
        The default maximum number of items a customer can add to his cart per product type.
        """
        return self._setting('SHOP_MAX_PURCHASE_QUANTITY', 99)

    @property
    def SHOP_SELL_SHORT_PERIOD(self):
        """
        The time period (in seconds or timedelta) from the current timestamp, in which a product
        is considered available, although it currently is not in stock, but scheduled to be added
        to the inventory.
        """
        from datetime import timedelta
        from django.core.exceptions import ImproperlyConfigured

        period = self._setting('SHOP_SELL_SHORT_PERIOD', 7 * 24 * 3600)
        if isinstance(period, int):
            period = timedelta(seconds=period)
        elif not isinstance(period, timedelta):
            raise ImproperlyConfigured("'SHOP_SELL_SHORT_PERIOD' contains an invalid property.")
        return period

    @property
    def SHOP_LIMITED_OFFER_PERIOD(self):
        """
        The time period (in seconds or timedelta) from the current timestamp, in which a product
        is marked as limited time offer.
        """
        from datetime import timedelta
        from django.core.exceptions import ImproperlyConfigured

        period = self._setting('SHOP_LIMITED_OFFER_PERIOD', 7 * 24 * 3600)
        if isinstance(period, int):
            period = timedelta(seconds=period)
        elif not isinstance(period, timedelta):
            raise ImproperlyConfigured("'SHOP_LIMITED_OFFER_PERIOD' contains an invalid property.")
        return period

    @property
    def SHOP_LINK_TO_EMPTY_CART(self):
        """
        If ``True`` the link on the cart-icon pointing to the cart is enabled, even if there are no
        items are in the cart.
        """
        return self._setting('SHOP_LINK_TO_EMPTY_CART', True)

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
                          'shop.serializers.defaults.order_item.OrderItemSerializer')
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
        return [import_string(mc) for mc in cart_modifiers]

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
    def SHOP_OVERRIDE_SHIPPING_METHOD(self):
        """
        If this directive is ``True``, the merchant is allowed to override the shipping method the
        customer has chosen while performing the checkout.

        Note that if alternative shipping is more expensive, usually the merchant has to come up
        for the additional costs.

        The default is ``False``.
        """
        return self._setting('SHOP_OVERRIDE_SHIPPING_METHOD', False)

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
        This allows the usage of the endpoint ``resolve('shop:checkout-upload')`` in a generic way.

        If Cascade plugins are used for the forms in the checkout view, this list can be empty.
        """
        return self._setting('SHOP_DIALOG_FORMS', [])

    @property
    def SHOP_CASCADE_FORMS(self):
        """
        Specify a map of Django Form classes to be used by the Cascade plugins used for the
        checkout view. Override this map, if the Cascade plugins shall use a Form other than the
        ones provided.
        """
        cascade_forms = {
            'CustomerForm': 'shop.forms.checkout.CustomerForm',
            'GuestForm': 'shop.forms.checkout.GuestForm',
            'ShippingAddressForm': 'shop.forms.checkout.ShippingAddressForm',
            'BillingAddressForm': 'shop.forms.checkout.BillingAddressForm',
            'PaymentMethodForm': 'shop.forms.checkout.PaymentMethodForm',
            'ShippingMethodForm': 'shop.forms.checkout.ShippingMethodForm',
            'ExtraAnnotationForm': 'shop.forms.checkout.ExtraAnnotationForm',
            'AcceptConditionForm': 'shop.forms.checkout.AcceptConditionForm',
            'RegisterUserForm': 'shop.forms.auth.RegisterUserForm',
        }
        cascade_forms.update(self._setting('SHOP_CASCADE_FORMS', {}))
        return cascade_forms

    def __getattr__(self, key):
        if not key.startswith('SHOP_'):
            key = 'SHOP_' + key
        return self.__getattribute__(key)

app_settings = DefaultSettings()
