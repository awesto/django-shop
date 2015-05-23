# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Max
from django.forms import fields
from django.template.loader import select_template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from shop import settings as shop_settings
from shop.models.cart import CartModel
from shop.modifiers.pool import cart_modifiers_pool
from .plugin_base import ShopLinkPluginBase, DialogFormPluginBase


class ProceedButtonForm(LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)

    button_content = fields.CharField(required=False, label=_("Content"),
                                      help_text=_("Proceed buttons content"))

    def clean(self):
        cleaned_data = super(ProceedButtonForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary'].update(button_content=cleaned_data['button_content'])
        return cleaned_data


class ShopProceedButton(BootstrapButtonMixin, ShopLinkPluginBase):
    """
    This button is used to proceed from one checkout step to the next one.
    """
    name = _("Proceed Button")
    form = ProceedButtonForm
    parent_classes = ('BootstrapColumnPlugin',)
    model_mixins = (LinkElementMixin,)
    fields = ('button_content', ('link_type', 'cms_page'), 'glossary',)
    glossary_field_map = {'link': ('link_type', 'cms_page',)}

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('button_content', ''))

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/proceed-button.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/proceed-button.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopProceedButton)


class CustomerFormPlugin(DialogFormPluginBase):
    """
    provides the form to edit customer specific data stored in model `Customer`.
    """
    name = _("Customer Form")
    form_class = 'shop.forms.checkout.CustomerForm'
    template_leaf_name = 'customer.html'

    def get_form_data(self, request):
        return {'instance': request.user}

DialogFormPluginBase.register_plugin(CustomerFormPlugin)


class GuestFormPlugin(CustomerFormPlugin):
    name = _("Guest Form")
    form_class = 'shop.forms.checkout.GuestForm'

DialogFormPluginBase.register_plugin(GuestFormPlugin)


class CheckoutAddressPluginBase(DialogFormPluginBase):
    def get_form_data(self, request):
        filter_args = {'user': request.user, '{}__isnull'.format(self.FormClass.priority_field): False}
        AddressModel = self.FormClass.get_model()
        address = AddressModel.objects.filter(**filter_args).order_by(self.FormClass.priority_field).first()
        if address:
            return {'instance': address}
        else:
            aggr = AddressModel.objects.filter(user=request.user).aggregate(Max(self.FormClass.priority_field))
            initial = {'priority': aggr['{}__max'.format(self.FormClass.priority_field)] or 0}
            return {'initial': initial}


class ShippingAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Shipping Address Form")
    form_class = 'shop.forms.checkout.ShippingAddressForm'
    template_leaf_name = 'shipping-address.html'

DialogFormPluginBase.register_plugin(ShippingAddressFormPlugin)


class BillingAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Billing Address Form")
    form_class = 'shop.forms.checkout.BillingAddressForm'
    template_leaf_name = 'billing-address.html'

DialogFormPluginBase.register_plugin(BillingAddressFormPlugin)


class PaymentMethodFormPlugin(DialogFormPluginBase):
    name = _("Payment Method Form")
    form_class = 'shop.forms.checkout.PaymentMethodForm'
    template_leaf_name = 'payment-method.html'

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        initial = {'payment_modifier': cart.extra.get('payment_modifier')}
        return {'initial': initial}

    def render(self, context, instance, placeholder):
        super(PaymentMethodFormPlugin, self).render(context, instance, placeholder)
        for payment_modifier in cart_modifiers_pool.get_payment_modifiers():
            payment_modifier.update_render_context(context)
        return context

if cart_modifiers_pool.get_payment_modifiers():
    # Plugin is registered only if at least one payment modifier exists
    DialogFormPluginBase.register_plugin(PaymentMethodFormPlugin)


class ShippingMethodFormPlugin(DialogFormPluginBase):
    name = _("Shipping Method Form")
    form_class = 'shop.forms.checkout.ShippingMethodForm'
    template_leaf_name = 'shipping-method.html'

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.shipping_method}

    def render(self, context, instance, placeholder):
        super(ShippingMethodFormPlugin, self).render(context, instance, placeholder)
        for shipping_modifier in cart_modifiers_pool.get_shipping_modifiers():
            shipping_modifier.update_render_context(context)
        return context

if cart_modifiers_pool.get_shipping_modifiers():
    # Plugin is registered only if at least one shipping modifier exists
    DialogFormPluginBase.register_plugin(ShippingMethodFormPlugin)


class ExtrasFormPlugin(DialogFormPluginBase):
    name = _("Extra Annotation Form")
    form_class = 'shop.forms.checkout.ExtrasForm'
    template_leaf_name = 'extras.html'

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
    template_leaf_name = 'terms-and-conditions.html'

DialogFormPluginBase.register_plugin(TermsAndConditionsFormPlugin)
