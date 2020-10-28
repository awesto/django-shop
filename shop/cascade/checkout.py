from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms import fields, widgets
from django.template import engines
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.cms_plugins import TextPlugin
from cmsplugin_cascade.bootstrap4.buttons import ButtonFormMixin
from cmsplugin_cascade.strides import strides_plugin_map, strides_element_map, TextStridePlugin, TextStrideElement
from cmsplugin_cascade.icon.forms import IconFormMixin
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.plugin_base import TransparentContainer
from cmsplugin_cascade.bootstrap4.buttons import BootstrapButtonMixin
from shop.cascade.plugin_base import ShopPluginBase, DialogFormPluginBase, DialogPluginBaseForm
from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.modifiers.pool import cart_modifiers_pool


class ProceedButtonFormMixin(LinkFormMixin, IconFormMixin, ButtonFormMixin):
    require_icon = False

    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('NEXT_STEP', _("Next Step")),
        ('RELOAD_PAGE', _("Reload Page")),
        ('PURCHASE_NOW', _("Purchase Now")),
        ('DO_NOTHING', _("Do nothing")),
    ]

    disable_invalid = fields.BooleanField(
        label=_("Disable if invalid"),
        required=False,
        help_text=_("Disable button if any form in this set is invalid."),
    )

    class Meta:
        entangled_fields = {'glossary': ['disable_invalid']}


class ShopProceedButton(BootstrapButtonMixin, LinkPluginBase):
    """
    This button is used to proceed from one checkout step to the next one.
    """
    name = _("Proceed Button")
    parent_classes = ['BootstrapColumnPlugin', 'ProcessStepPlugin', 'ValidateSetOfFormsPlugin']
    form = ProceedButtonFormMixin
    model_mixins = (LinkElementMixin,)
    ring_plugin = 'ProceedButtonPlugin'

    class Media:
        js = ['admin/js/jquery.init.js', 'shop/js/admin/proceedbuttonplugin.js']

    @classmethod
    def get_identifier(cls, instance):
        return mark_safe(instance.glossary.get('link_content', ''))

    def get_render_template(self, context, instance, placeholder):
        if instance.link == 'NEXT_STEP':
            button_template = 'next-step-button'
        elif instance.link == 'RELOAD_PAGE':
            button_template = 'reload-button'
        elif instance.link == 'PURCHASE_NOW':
            button_template = 'purchase-button'
        elif instance.link == 'DO_NOTHING':
            button_template = 'noop-button'
        else:
            button_template = 'proceed-button'
        template_names = [
            '{}/checkout/{}.html'.format(app_settings.APP_LABEL, button_template),
            'shop/checkout/{}.html'.format(button_template),
        ]
        return select_template(template_names)

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
    form_class = app_settings.SHOP_CASCADE_FORMS['CustomerForm']

    def render(self, context, instance, placeholder):
        if not context['request'].customer.is_registered:
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
    form_class = app_settings.SHOP_CASCADE_FORMS['GuestForm']

    def render(self, context, instance, placeholder):
        assert 'customer' in context, "Please add 'shop.context_processors.customer' to your TEMPLATES 'context_processor' settings."
        if not context['customer'].is_guest:
            context['error_message'] = _("Only guest customers can access this form.")
            return context
        return self.super(GuestFormPlugin, self).render(context, instance, placeholder)

DialogFormPluginBase.register_plugin(GuestFormPlugin)


class CheckoutAddressPluginForm(DialogPluginBaseForm):
    ADDRESS_CHOICES = [
        ('shipping', _("Shipping")),
        ('billing', _("Billing")),
    ]

    address_form = fields.ChoiceField(
        choices=ADDRESS_CHOICES,
        widget=widgets.RadioSelect,
        label=_("Address Form"),
        initial=ADDRESS_CHOICES[0][0]
    )

    allow_multiple = fields.BooleanField(
        label=_("Multiple Addresses"),
        initial=False,
        required=False,
        help_text=_("Allow the customer to add and edit multiple addresses."),
    )

    allow_use_primary = fields.BooleanField(
        label=_("Use primary address"),
        initial=False,
        required=False,
        help_text=_("Allow the customer to use the primary address, if this is the secondary form."),
    )

    class Meta:
        entangled_fields = {'glossary': ['address_form', 'allow_multiple', 'allow_use_primary']}


class CheckoutAddressPlugin(DialogFormPluginBase):
    name = _("Checkout Address Form")
    form = CheckoutAddressPluginForm
    # glossary_field_order = ['address_form', 'render_type', 'allow_multiple', 'allow_use_primary', 'headline_legend']
    form_classes = [app_settings.SHOP_CASCADE_FORMS['ShippingAddressForm'], app_settings.SHOP_CASCADE_FORMS['BillingAddressForm']]

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
        if form_data.get('cart') is None:
            raise PermissionDenied("Can not proceed to checkout without cart")

        address = self.get_address(form_data['cart'], instance)
        if instance.glossary.get('allow_multiple'):
            form_data.update(multi_addr=True)
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
        identifier = super().get_identifier(instance)
        address_form = instance.glossary.get('address_form')
        address_form = dict(cls.form.ADDRESS_CHOICES).get(address_form, '')
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


class MethodPluginForm(DialogPluginBaseForm):
    show_additional_charge = fields.BooleanField(
        label=_("Show additional charge"),
        initial=True,
        required=False,
        help_text=_("Add an extra line showing the additional charge depending on the chosen payment/shipping method."),
    )

    class Meta:
        entangled_fields = {'glossary': ['show_additional_charge']}


class PaymentMethodFormPlugin(DialogFormPluginBase):
    name = _("Payment Method Form")
    form = MethodPluginForm
    form_class = app_settings.SHOP_CASCADE_FORMS['PaymentMethodForm']
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
        context['show_additional_charge'] = instance.glossary.get('show_additional_charge', False)
        return context

if cart_modifiers_pool.get_payment_modifiers():
    # Plugin is registered only if at least one payment modifier exists
    DialogFormPluginBase.register_plugin(PaymentMethodFormPlugin)


class ShippingMethodFormPlugin(DialogFormPluginBase):
    name = _("Shipping Method Form")
    form = MethodPluginForm
    form_class = app_settings.SHOP_CASCADE_FORMS['ShippingMethodForm']
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
        context['show_additional_charge'] = instance.glossary.get('show_additional_charge', False)
        return context

if cart_modifiers_pool.get_shipping_modifiers():
    # Plugin is registered only if at least one shipping modifier exists
    DialogFormPluginBase.register_plugin(ShippingMethodFormPlugin)


class ExtraAnnotationFormPlugin(DialogFormPluginBase):
    name = _("Extra Annotation Form")
    form_class = app_settings.SHOP_CASCADE_FORMS['ExtraAnnotationForm']
    template_leaf_name = 'extra-annotation-{}.html'

    def get_form_data(self, context, instance, placeholder):
        form_data = self.super(ExtraAnnotationFormPlugin, self).get_form_data(context, instance, placeholder)
        cart = form_data.get('cart')
        if cart:
            form_data.update(initial={'annotation': cart.extra.get('annotation', '')})
        return form_data

DialogFormPluginBase.register_plugin(ExtraAnnotationFormPlugin)


class AcceptConditionMixin:
    render_template = 'shop/checkout/accept-condition.html'

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
        try:
            FormClass = import_string(app_settings.SHOP_CASCADE_FORMS['AcceptConditionForm'])
        except ImportError:
            msg = "Can not import Form class. Please check your settings directive SHOP_CASCADE_FORMS['AcceptConditionForm']."
            raise ImproperlyConfigured(msg)
        form_data = {'cart': cart, 'initial': dict(plugin_id=instance.pk, plugin_order=request._plugin_order)}
        bound_form = FormClass(**form_data)
        context[bound_form.form_name] = bound_form
        super().render(context, instance, placeholder)
        accept_condition_form = context['accept_condition_form.plugin_{}'.format(instance.pk)]
        # transfer the stored HTML content into the widget's label
        accept_condition_form['accept'].field.label = mark_safe(context['body'])
        accept_condition_form['accept'].field.widget.choice_label = accept_condition_form['accept'].field.label  # Django < 1.11
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
    name = _("Manage Set of Forms")
    allow_children = True
    alien_child_classes = True

    def get_render_template(self, context, instance, placeholder):
        return select_template([
            '{}/checkout/forms-set.html'.format(app_settings.APP_LABEL),
            'shop/checkout/forms-set.html',
        ])

plugin_pool.register_plugin(ValidateSetOfFormsPlugin)
