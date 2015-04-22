# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import get_model, Max
from django.forms import fields
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.utils import resolve_dependencies
from shop import settings as shop_settings
from shop.models.auth import get_customer
from shop.models.cart import CartModel
from shop.rest.serializers import CartSerializer
from shop.modifiers.pool import cart_modifiers_pool
from .plugin_base import ShopPluginBase, DialogFormPluginBase, ButtonPluginBase


class ShopCheckoutSummaryPlugin(ShopPluginBase):
    """
    Renders a read-only summary of the cart to be displayed during the checkout.
    """
    name = _("Checkout Summary")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

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


class ProceedButtonForm(LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)

    button_content = fields.CharField(required=False, label=_("Content"),
                                      help_text=_("Proceed buttons content"))

    def clean(self):
        cleaned_data = super(ProceedButtonForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary'].update(button_content=cleaned_data['button_content'])
        return cleaned_data


class ShopProceedButton(ButtonPluginBase):
    """
    This button is used to proceed from one checkout step to the next one.
    """
    name = _("Proceed Button")
    form = ProceedButtonForm
    parent_classes = ('BootstrapColumnPlugin',)
    model_mixins = (LinkElementMixin,)
    fields = ('button_content', ('link_type', 'cms_page'), 'glossary',)
    glossary_field_map = {'link': ('link_type', 'cms_page',)}
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options', 'quick-float',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if link.get('type') == 'cmspage':
            if 'model' in link and 'pk' in link:
                if not hasattr(obj, '_link_model'):
                    Model = get_model(*link['model'].split('.'))
                    try:
                        obj._link_model = Model.objects.get(pk=link['pk'])
                    except Model.DoesNotExist:
                        obj._link_model = None
                if obj._link_model:
                    return obj._link_model.get_absolute_url()
        else:
            # use the link type as special action keyword
            return link.get('type')

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/proceed-button.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/proceed-button.html',
        ]
        return select_template(template_names)

    def get_ring_bases(self):
        bases = super(ShopProceedButton, self).get_ring_bases()
        bases.append('LinkPluginBase')
        return bases

plugin_pool.register_plugin(ShopProceedButton)


class CustomerFormPlugin(DialogFormPluginBase):
    """
    provides the form to edit customer specific data stored in model `Customer`.
    """
    name = _("Customer Form")
    cache = False
    form_class = 'shop.forms.checkout.CustomerForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/customer.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/customer.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        return {'instance': get_customer(request)}

DialogFormPluginBase.register_plugin(CustomerFormPlugin)


class CheckoutAddressPluginBase(DialogFormPluginBase):
    def get_form_data(self, request):
        user = get_customer(request)
        filter_args = {'user': user, '{}__isnull'.format(self.FormClass.priority_field): False}
        AddressModel = self.FormClass.get_model()
        address = AddressModel.objects.filter(**filter_args).order_by(self.FormClass.priority_field).first()
        if address:
            return {'instance': address}
        else:
            aggr = AddressModel.objects.filter(user=user).aggregate(Max(self.FormClass.priority_field))
            initial = {'priority': aggr['{}__max'.format(self.FormClass.priority_field)] or 0}
            return {'initial': initial}


class ShippingAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Shipping Address Dialog")
    form_class = 'shop.forms.checkout.ShippingAddressForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/shipping-address.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/shipping-address.html',
        ]
        return select_template(template_names)

DialogFormPluginBase.register_plugin(ShippingAddressFormPlugin)


class InvoiceAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Invoice Address Dialog")
    form_class = 'shop.forms.checkout.InvoiceAddressForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/invoice-address.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/invoice-address.html',
        ]
        return select_template(template_names)

DialogFormPluginBase.register_plugin(InvoiceAddressFormPlugin)


class PaymentMethodFormPlugin(DialogFormPluginBase):
    name = _("Payment Method Dialog")
    form_class = 'shop.forms.checkout.PaymentMethodForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/payment-method.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/payment-method.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.payment_method}

if cart_modifiers_pool.get_payment_modifiers():
    # Plugin is registered only if at least one payment modifier exists
    DialogFormPluginBase.register_plugin(PaymentMethodFormPlugin)


class ShippingMethodFormPlugin(DialogFormPluginBase):
    name = _("Shipping Method Dialog")
    form_class = 'shop.forms.checkout.ShippingMethodForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/shipping-method.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/shipping-method.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.shipping_method}

if cart_modifiers_pool.get_shipping_modifiers():
    # Plugin is registered only if at least one shipping modifier exists
    DialogFormPluginBase.register_plugin(ShippingMethodFormPlugin)


class ExtrasFormPlugin(DialogFormPluginBase):
    name = _("Extras Dialog")
    form_class = 'shop.forms.checkout.ExtrasForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/extras.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/extras.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.extras or {}}

DialogFormPluginBase.register_plugin(ExtrasFormPlugin)


class TermsAndConditionsFormPlugin(DialogFormPluginBase):
    """
    Provides the form to accept terms and conditions.
    """
    name = _("Terms and Conditions")
    form_class = 'shop.forms.checkout.TermsAndConditionsForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/terms-and-conditions.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/terms-and-conditions.html',
        ]
        return select_template(template_names)

DialogFormPluginBase.register_plugin(TermsAndConditionsFormPlugin)
