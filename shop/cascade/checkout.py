# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.forms.fields import CharField
from django.forms import widgets
from django.template import engines
from django.template.loader import select_template
from django.utils.html import strip_tags, format_html
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from cms.plugin_pool import plugin_pool

from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.utils import plugin_tags_to_user_html
from djangocms_text_ckeditor.cms_plugins import TextPlugin

from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.strides import strides_plugin_map, strides_element_map, TextStridePlugin, TextStrideElement
from cmsplugin_cascade.link.cms_plugins import TextLinkPlugin
from cmsplugin_cascade.link.forms import LinkForm, TextLinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.plugin_base import TransparentContainer
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin

from shop.conf import app_settings
from shop.forms.checkout import AcceptConditionForm
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
    form = ProceedButtonForm
    glossary_field_order = ('button_type', 'button_size', 'button_options', 'quick_float',
                            'icon_align', 'icon_font', 'symbol')
    ring_plugin = 'ProceedButtonPlugin'

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css',
                       'cascade/css/admin/bootstrap-theme.min.css',
                       'cascade/css/admin/iconplugin.css',)}
        js = ['shop/js/admin/proceedbuttonplugin.js']

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/proceed-button.html'.format(app_settings.APP_LABEL),
            'shop/checkout/proceed-button.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        self.super(ShopProceedButton, self).render(context, instance, placeholder)
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
        form_data = self.super(CustomerFormPluginBase, self).get_form_data(context, instance, placeholder)
        form_data.update(instance=context['request'].customer)
        return form_data

    def get_render_template(self, context, instance, placeholder):
        if 'error_message' in context:
            return engines['django'].from_string('<p class="text-danger">{{ error_message }}</p>')
        return self.super(CustomerFormPluginBase, self).get_render_template(context, instance, placeholder)


class CustomerFormPlugin(CustomerFormPluginBase):
    """
    Provides the form to edit specific data stored in :class:`shop.model.customer.CustomerModel`,
    if customer declared himself as registered.
    """
    name = _("Customer Form")
    form_class = 'shop.forms.checkout.CustomerForm'

    def render(self, context, instance, placeholder):
        if not context['request'].customer.is_registered():
            context['error_message'] = _("Only registered customers can access this form.")
            return context
        return self.super(CustomerFormPlugin, self).render(context, instance, placeholder)

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
        return self.super(GuestFormPlugin, self).render(context, instance, placeholder)

DialogFormPluginBase.register_plugin(GuestFormPlugin)


class CheckoutAddressPlugin(DialogFormPluginBase):
    name = _("Checkout Address Form")
    glossary_field_order = ['address_form', 'render_type', 'allow_multiple', 'allow_use_primary', 'headline_legend']
    form_classes = ['shop.forms.checkout.ShippingAddressForm', 'shop.forms.checkout.BillingAddressForm']
    ADDRESS_CHOICES = [('shipping', _("Shipping")), ('billing', _("Billing"))]

    address_form = GlossaryField(
        widgets.RadioSelect(choices=ADDRESS_CHOICES),
        label=_("Address Form"),
        initial=ADDRESS_CHOICES[0][0]
    )

    allow_multiple = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Multiple Addresses"),
        initial=False,
        help_text=_("Allow the customer to add and edit multiple addresses."),
    )

    allow_use_primary = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Use primary address"),
        initial=False,
        help_text=_("Allow the customer to use the primary address, if this is the secondary form."),
    )

    def get_form_class(self, instance):
        if instance.glossary.get('address_form') == 'shipping':
            return import_string(self.form_classes[0])
        else:  # address_form == billing
            return import_string(self.form_classes[1])

    def get_address(self, cart, instance):
        if instance.glossary.get('address_form') == 'shipping':
            if cart.shipping_address:
                address = cart.shipping_address
            else:
                # fallback to another existing shipping address
                FormClass = self.get_form_class(instance)
                address = FormClass.get_model().objects.get_fallback(customer=cart.customer)
        else:  # address_form == billing
            if cart.billing_address:
                address = cart.billing_address
            else:
                # fallback to another existing billing address
                FormClass = self.get_form_class(instance)
                address = FormClass.get_model().objects.get_fallback(customer=cart.customer)
        return address

    def get_form_data(self, context, instance, placeholder):
        form_data = self.super(CheckoutAddressPlugin, self).get_form_data(context, instance, placeholder)
        if form_data['cart'] is None:
            raise PermissionDenied("Can not proceed to checkout without cart")

        address = self.get_address(form_data['cart'], instance)
        if instance.glossary.get('allow_multiple'):
            AddressModel = self.get_form_class(instance).get_model()
            addresses = AddressModel.objects.filter(customer=context['request'].customer).order_by('priority')
            form_entities = []
            for number, addr in enumerate(addresses, 1):
                form_entities.append({
                    'value': str(addr.priority),
                    'label': "{}. {}".format(number, addr.as_text().strip().replace('\n', ' – '))
                })
            form_data.update(multi_addr=True, form_entities=form_entities)
        else:
            form_data.update(multi_addr=False)

        form_data.update(
            instance=address,
            initial={'active_priority': address.priority if address else 'add'},
            allow_use_primary=instance.glossary.get('allow_use_primary', False)
        )
        return form_data

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(CheckoutAddressPlugin, cls).get_identifier(instance)
        address_form = instance.glossary.get('address_form')
        address_form = dict(cls.ADDRESS_CHOICES).get(address_form, '')
        return format_html(pgettext_lazy('get_identifier', "for {} {}"), address_form, identifier)

    def get_render_template(self, context, instance, placeholder):
        addr_form = instance.glossary.get('address_form')
        if addr_form not in ['shipping', 'billing']:  # validate
            addr_form = 'shipping'
        render_type = instance.glossary.get('render_type')
        if render_type not in ['form', 'summary']:  # validate
            render_type = 'form'
        template_names = [
            '{0}/checkout/{1}-address-{2}.html'.format(app_settings.APP_LABEL, addr_form, render_type),
            'shop/checkout/{0}-address-{1}.html'.format(addr_form, render_type),
        ]
        return select_template(template_names)

DialogFormPluginBase.register_plugin(CheckoutAddressPlugin)


class PaymentMethodFormPlugin(DialogFormPluginBase):
    name = _("Payment Method Form")
    form_class = 'shop.forms.checkout.PaymentMethodForm'
    template_leaf_name = 'payment-method-{}.html'

    def get_form_data(self, context, instance, placeholder):
        form_data = self.super(PaymentMethodFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'payment_modifier': cart.extra.get('payment_modifier')})
        return form_data

    def render(self, context, instance, placeholder):
        self.super(PaymentMethodFormPlugin, self).render(context, instance, placeholder)
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
        form_data = self.super(ShippingMethodFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'shipping_modifier': cart.extra.get('shipping_modifier')})
        return form_data

    def render(self, context, instance, placeholder):
        self.super(ShippingMethodFormPlugin, self).render(context, instance, placeholder)
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
        form_data = self.super(ExtraAnnotationFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'annotation': cart.extra.get('annotation', '')})
        return form_data

DialogFormPluginBase.register_plugin(ExtraAnnotationFormPlugin)


class AcceptConditionFormPlugin(DialogFormPluginBase):
    """
    Deprecated. Use AcceptConditionPlugin instead.
    """
    name = _("Accept Condition (deprecated)")
    form_class = 'shop.forms.checkout.AcceptConditionForm'
    template_leaf_name = 'accept-condition.html'
    html_parser = HTMLParser()
    change_form_template = 'cascade/admin/text_plugin_change_form.html'

    @classmethod
    def get_identifier(cls, instance):
        html_content = cls.html_parser.unescape(instance.glossary.get('html_content', ''))
        html_content = strip_tags(html_content)
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
        self.super(AcceptConditionFormPlugin, self).render(context, instance, placeholder)
        accept_condition_form = context['accept_condition_form.plugin_{}'.format(instance.id)]
        html_content = self.html_parser.unescape(instance.glossary.get('html_content', ''))
        html_content = plugin_tags_to_user_html(html_content, context)
        # transfer the stored HTML content into the widget's label
        accept_condition_form['accept'].field.widget.choice_label = mark_safe(html_content)
        context['accept_condition_form'] = accept_condition_form
        return context

# DialogFormPluginBase.register_plugin(AcceptConditionFormPlugin)

class AcceptConditionMixin(object):
    render_template = 'shop/checkout/accept-condition.html'
    FormClass = AcceptConditionForm

    def render(self, context, instance, placeholder):
        """
        Return the context to render a checkbox used to accept the terms and conditions
        """
        request = context['request']
        try:
            cart = CartModel.objects.get_from_request(request)
            cart.update(request)
        except CartModel.DoesNotExist:
            cart = None
        request._plugin_order = getattr(request, '_plugin_order', 0) + 1
        form_data = {'cart': cart, 'initial': dict(plugin_id=instance.pk, plugin_order=request._plugin_order)}
        bound_form = self.FormClass(**form_data)
        context[bound_form.form_name] = bound_form
        super(AcceptConditionMixin, self).render(context, instance, placeholder)
        accept_condition_form = context['accept_condition_form.plugin_{}'.format(instance.pk)]
        # transfer the stored HTML content into the widget's label
        accept_condition_form['accept'].field.widget.choice_label = mark_safe(context['body'])
        context['accept_condition_form'] = accept_condition_form
        return context


class AcceptConditionPlugin(AcceptConditionMixin, TextPlugin):
    name = _("Accept Condition")
    module = "Shop"

    def get_admin_url_name(self, name):
        model_name = 'acceptcondition'
        url_name = "%s_%s_%s" % ('shop', model_name, name)
        return url_name


class AcceptConditionMinion(AcceptConditionMixin, TextStridePlugin):
    pass

plugin_pool.register_plugin(AcceptConditionPlugin)
strides_plugin_map['AcceptConditionPlugin'] = AcceptConditionMinion
strides_element_map['AcceptConditionPlugin'] = TextStrideElement


class RequiredFormFieldsPlugin(ShopPluginBase):
    """
    This plugin renders a short text message, emphasizing that fields with a star are required.
    """
    name = _("Required Form Fields")
    template_leaf_name = 'required-form-fields.html'
    parent_classes = ('BootstrapColumnPlugin',)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{0}/checkout/{1}'.format(app_settings.APP_LABEL, self.template_leaf_name),
            'shop/checkout/{}'.format(self.template_leaf_name),
        ]
        return select_template(template_names)

plugin_pool.register_plugin(RequiredFormFieldsPlugin)


class ValidateSetOfFormsPlugin(TransparentContainer, ShopPluginBase):
    """
    This plugin wraps arbitrary forms into the Angular directive shopFormsSet.
    This is required to validate all forms, so that a proceed button is disabled otherwise.
    """
    name = _("Validate Set of Forms")
    allow_children = True
    alien_child_classes = True

    def get_render_template(self, context, instance, placeholder):
        return select_template([
            '{}/checkout/forms-set.html'.format(app_settings.APP_LABEL),
            'shop/checkout/forms-set.html',
        ])

plugin_pool.register_plugin(ValidateSetOfFormsPlugin)
