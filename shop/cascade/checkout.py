# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.fields import CharField
from django.forms import widgets
from django.template import Engine
from django.template.loader import select_template
from django.utils.html import strip_tags, strip_entities
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.utils import plugin_tags_to_user_html
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.link.cms_plugins import TextLinkPlugin
from cmsplugin_cascade.link.forms import LinkForm, TextLinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.mixins import TransparentMixin
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from shop import settings as shop_settings
from shop.models.cart import CartModel
from shop.modifiers.pool import cart_modifiers_pool
from .plugin_base import ShopPluginBase, ShopButtonPluginBase, DialogFormPluginBase


class ProceedButtonForm(TextLinkFormMixin, LinkForm):
    link_content = CharField(label=_("Button Content"))
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")),
        ('PURCHASE_NOW', _("Purchase Now")),)


class ShopProceedButton(BootstrapButtonMixin, ShopButtonPluginBase):
    """
    This button is used to proceed from one checkout step to the next one.
    """
    name = _("Proceed Button")
    parent_classes = ('BootstrapColumnPlugin', 'ProcessStepPlugin', 'ValidateSetOfFormsPlugin')
    model_mixins = (LinkElementMixin,)
    glossary_field_order = ('button_type', 'button_size', 'button_options', 'quick_float',
                            'icon_left', 'icon_right')

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(form=ProceedButtonForm)
        return super(ShopProceedButton, self).get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/proceed-button.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/proceed-button.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        super(ShopProceedButton, self).render(context, instance, placeholder)
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            cart.update(context['request'])
            context['cart'] = cart
        except CartModel.DoesNotExist:
            pass
        return context

plugin_pool.register_plugin(ShopProceedButton)


class CustomerFormPluginBase(DialogFormPluginBase):
    """
    Base class for CustomerFormPlugin and GuestFormPlugin to share common methods.
    """
    template_leaf_name = 'customer-{}.html'
    cache = False

    def get_form_data(self, context, instance, placeholder):
        form_data = super(CustomerFormPluginBase, self).get_form_data(context, instance, placeholder)
        form_data.update(instance=context['request'].customer)
        return form_data

    def get_render_template(self, context, instance, placeholder):
        if 'error_message' in context:
            return Engine().from_string('<p class="text-danger">{{ error_message }}</p>')
        return super(CustomerFormPluginBase, self).get_render_template(context, instance, placeholder)


class CustomerFormPlugin(CustomerFormPluginBase):
    """
    Provides the form to edit specific data stored in model `Customer`, if customer declared
    himself as registered.
    """
    name = _("Customer Form")
    form_class = 'shop.forms.checkout.CustomerForm'

    def render(self, context, instance, placeholder):
        if not context['request'].customer.is_registered():
            context['error_message'] = _("Only registered customers can access this form.")
            return context
        return super(CustomerFormPlugin, self).render(context, instance, placeholder)

DialogFormPluginBase.register_plugin(CustomerFormPlugin)


class GuestFormPlugin(CustomerFormPluginBase):
    """
    Provides the form to edit specific data stored in model `Customer`, if customer declared
    himself as guest.
    """
    name = _("Guest Form")
    form_class = 'shop.forms.checkout.GuestForm'

    def render(self, context, instance, placeholder):
        if not context['customer'].is_guest():
            context['error_message'] = _("Only guest customers can access this form.")
            return context
        return super(GuestFormPlugin, self).render(context, instance, placeholder)

DialogFormPluginBase.register_plugin(GuestFormPlugin)


class CheckoutAddressPluginBase(DialogFormPluginBase):
    multi_addr = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Multiple Addresses"),
        initial=False,
        help_text=_("Shall the customer be allowed to edit multiple addresses."),
    )

    def get_form_data(self, context, instance, placeholder):
        form_data = super(CheckoutAddressPluginBase, self).get_form_data(context, instance, placeholder)

        AddressModel = self.FormClass.get_model()
        assert form_data['cart'] is not None, "Can not proceed to checkout without cart"
        address = self.get_address(form_data['cart'])
        form_data.update(instance=address)

        if instance.glossary.get('multi_addr'):
            addresses = AddressModel.objects.filter(customer=context['request'].customer).order_by('priority')
            form_entities = [dict(value=str(addr.priority),
                            label="{}. {}".format(number, addr.as_text().replace('\n', ' – ')))
                             for number, addr in enumerate(addresses, 1)]
            form_data.update(multi_addr=True, form_entities=form_entities)
        else:
            form_data.update(multi_addr=False)
        return form_data


class ShippingAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Shipping Address Form")
    form_class = 'shop.forms.checkout.ShippingAddressForm'
    template_leaf_name = 'shipping-address-{}.html'

    def get_address(self, cart):
        if cart.shipping_address is None:
            # fallback to another existing shipping address
            address = self.FormClass.get_model().objects.get_fallback(customer=cart.customer)
            cart.shipping_address = address
            cart.save()
        return cart.shipping_address

DialogFormPluginBase.register_plugin(ShippingAddressFormPlugin)


class BillingAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Billing Address Form")
    form_class = 'shop.forms.checkout.BillingAddressForm'
    template_leaf_name = 'billing-address-{}.html'

    allow_use_shipping = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Use shipping address"),
        initial=True,
        help_text=_("Allow the customer to use the shipping address for billing."),
    )

    def get_address(self, cart):
        # if billing address is None, we use the shipping address
        return cart.billing_address

DialogFormPluginBase.register_plugin(BillingAddressFormPlugin)


class PaymentMethodFormPlugin(DialogFormPluginBase):
    name = _("Payment Method Form")
    form_class = 'shop.forms.checkout.PaymentMethodForm'
    template_leaf_name = 'payment-method-{}.html'

    def get_form_data(self, context, instance, placeholder):
        form_data = super(PaymentMethodFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'payment_modifier': cart.extra.get('payment_modifier')})
        return form_data

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
    template_leaf_name = 'shipping-method-{}.html'

    def get_form_data(self, context, instance, placeholder):
        form_data = super(ShippingMethodFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'shipping_modifier': cart.extra.get('shipping_modifier')})
        return form_data

    def render(self, context, instance, placeholder):
        super(ShippingMethodFormPlugin, self).render(context, instance, placeholder)
        for shipping_modifier in cart_modifiers_pool.get_shipping_modifiers():
            shipping_modifier.update_render_context(context)
        return context

if cart_modifiers_pool.get_shipping_modifiers():
    # Plugin is registered only if at least one shipping modifier exists
    DialogFormPluginBase.register_plugin(ShippingMethodFormPlugin)


class ExtraAnnotationFormPlugin(DialogFormPluginBase):
    name = _("Extra Annotation Form")
    form_class = 'shop.forms.checkout.ExtraAnnotationForm'
    template_leaf_name = 'extra-annotation-{}.html'

    def get_form_data(self, context, instance, placeholder):
        form_data = super(ExtraAnnotationFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'annotation': cart.extra.get('annotation', '')})
        return form_data

DialogFormPluginBase.register_plugin(ExtraAnnotationFormPlugin)


class AcceptConditionFormPlugin(DialogFormPluginBase):
    """
    Provides the form to accept any condition.
    """
    name = _("Accept Condition")
    form_class = 'shop.forms.checkout.AcceptConditionForm'
    template_leaf_name = 'accept-condition.html'
    html_parser = HTMLParser()
    change_form_template = 'cascade/admin/text_plugin_change_form.html'

    @classmethod
    def get_identifier(cls, instance):
        html_content = cls.html_parser.unescape(instance.glossary.get('html_content', ''))
        html_content = strip_entities(strip_tags(html_content))
        html_content = Truncator(html_content).words(3, truncate=' ...')
        return mark_safe(html_content)

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            html_content = self.html_parser.unescape(obj.glossary.get('html_content', ''))
            obj.glossary.update(html_content=html_content)
            text_editor_widget = TextEditorWidget(installed_plugins=[TextLinkPlugin], pk=obj.pk,
                                           placeholder=obj.placeholder, plugin_language=obj.language)
            kwargs['glossary_fields'] = (
                GlossaryField(text_editor_widget, label=_("HTML content"), name='html_content'),
            )
        return super(AcceptConditionFormPlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        super(AcceptConditionFormPlugin, self).render(context, instance, placeholder)
        accept_condition_form = context['accept_condition_form.plugin_{}'.format(instance.id)]
        html_content = self.html_parser.unescape(instance.glossary.get('html_content', ''))
        html_content = plugin_tags_to_user_html(html_content, context, placeholder)
        # transfer the stored HTML content into the widget's label
        accept_condition_form['accept'].field.widget.choice_label = mark_safe(html_content)
        context['accept_condition_form'] = accept_condition_form
        return context

DialogFormPluginBase.register_plugin(AcceptConditionFormPlugin)


class RequiredFormFieldsPlugin(ShopPluginBase):
    """
    This plugin renders a short text message, emphasizing that fields with a star are required.
    """
    name = _("Required Form Fields")
    template_leaf_name = 'required-form-fields.html'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{0}/checkout/{1}'.format(shop_settings.APP_LABEL, self.template_leaf_name),
            'shop/checkout/{}'.format(self.template_leaf_name),
        ]
        return select_template(template_names)

plugin_pool.register_plugin(RequiredFormFieldsPlugin)


class ValidateSetOfFormsPlugin(TransparentMixin, ShopPluginBase):
    """
    This plugin wraps arbitrary forms into the Angular directive shopFormsSet.
    This is required to validate all forms, so that a proceed button is disabled otherwise.
    """
    name = _("Validate Set of Forms")
    allow_children = True
    alien_child_classes = True

    def get_render_template(self, context, instance, placeholder):
        return select_template([
            '{}/checkout/forms-set.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/forms-set.html',
        ])

plugin_pool.register_plugin(ValidateSetOfFormsPlugin)
