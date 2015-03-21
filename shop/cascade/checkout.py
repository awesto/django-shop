# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Max
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.utils.module_loading import import_by_path
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.fields import PartialFormField
from shop import settings as shop_settings
from shop.models.cart import CartModel
from shop.rest.serializers import CartSerializer
from shop.modifiers.pool import cart_modifiers_pool


class ShopCheckoutSummaryPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout Summary")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    @classmethod
    def get_identifier(cls, obj):
        return force_text(cls.name)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/summary.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/summary.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        cart = CartModel.objects.get_from_request(context['request'])
        cart_serializer = CartSerializer(cart, context=context, label='checkout')
        context['cart'] = cart_serializer.data
        return super(ShopCheckoutSummaryPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutSummaryPlugin)


class ShopCheckoutAddressPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout Address")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    CHOICES = (('shipping', _("Shipping Address")), ('invoice', _("Invoice Address")),)
    glossary_fields = (
        PartialFormField('address_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Address type"),
            help_text=_("Use this address form for shipping or as invoice."),
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ShopCheckoutAddressPlugin, self).__init__(*args, **kwargs)
        self.ShippingAddressForm = import_by_path(shop_settings.SHIPPING_ADDRESS_FORM)
        self.InvoiceAddressForm = import_by_path(shop_settings.INVOICE_ADDRESS_FORM)

    @classmethod
    def get_identifier(cls, obj):
        address_type = obj.glossary.get('address_type')
        address_type = dict(cls.CHOICES).get(address_type)
        return force_text(address_type)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/address.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/address.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        if instance.glossary.get('address_type') == 'shipping':
            AddressForm = self.ShippingAddressForm
            priority_field = 'priority_shipping'
        else:
            AddressForm = self.InvoiceAddressForm
            priority_field = 'priority_invoice'
        user = context['request'].user
        AddressModel = AddressForm.get_model()
        filter_args = {'user': user, '{}__isnull'.format(priority_field): False}
        address = AddressModel.objects.filter(**filter_args).order_by(priority_field).first()
        if address:
            context['address'] = AddressForm(instance=address)
        else:
            aggr = AddressModel.objects.filter(user=user).aggregate(Max(priority_field))
            initial = {'priority': aggr['{}__max'.format(priority_field)] or 0}
            context['address'] = AddressForm(initial=initial)
        return super(ShopCheckoutAddressPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutAddressPlugin)


class ShopPaymentPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Payment Method")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = False

    def __init__(self, *args, **kwargs):
        super(ShopPaymentPlugin, self).__init__(*args, **kwargs)
        self.PaymentMethodForm = import_by_path(shop_settings.PAYMENT_METHOD_FORM)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            getattr(self.PaymentMethodForm, 'template_name', None),
            '{}/checkout/payment-method.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/payment-method.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        context['payment_method'] = self.PaymentMethodForm()  # TODO: set initial
        return super(ShopPaymentPlugin, self).render(context, instance, placeholder)

if cart_modifiers_pool.get_payment_choices():
    # Plugin is registered only if at least one payment modifier exists
    plugin_pool.register_plugin(ShopPaymentPlugin)


class ShopShippingPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Shipping Method")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = False

    def __init__(self, *args, **kwargs):
        super(ShopShippingPlugin, self).__init__(*args, **kwargs)
        self.ShippingMethodForm = import_by_path(shop_settings.SHIPPING_METHOD_FORM)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            getattr(self.ShippingMethodForm, 'template_name', None),
            '{}/checkout/shipping-method.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/shipping-method.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        context['shipping_method'] = self.ShippingMethodForm()  # TODO: set initial
        return super(ShopShippingPlugin, self).render(context, instance, placeholder)

if cart_modifiers_pool.get_shipping_choices():
    # Plugin is registered only if at least one shipping modifier exists
    plugin_pool.register_plugin(ShopShippingPlugin)


class ShopCheckoutButton(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout Button")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = False
    # text_enabled = True
    glossary_fields = (
        PartialFormField('button_content',
            widgets.Input(),
            label=_('Button Content'),
            help_text=_("Display Buy Buttom")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        content = obj.glossary.get('button_content', _("No content"))
        return force_text(content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/button.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/button.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        return super(ShopCheckoutButton, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutButton)
