# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model, Max
from django.forms import fields
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.module_loading import import_by_path
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
from .plugin_base import ShopPluginBase


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


class ButtonForm(LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")),)

    button_content = fields.CharField(required=False, label=_("Content"),
                                      help_text=_("Proceed buttons content"))

    def clean(self):
        cleaned_data = super(ButtonForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary'].update(button_content=cleaned_data['button_content'])
        return cleaned_data


class ShopProceedButton(ShopPluginBase):
    """
    This button is used to proceed from one checkout step to the next one.
    """
    module = 'Shop'
    name = _("Proceed Button")
    form = ButtonForm
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = False
    model_mixins = (LinkElementMixin,)
    fields = ('button_content', ('link_type', 'cms_page'), 'glossary',)
    glossary_field_map = {'link': ('link_type', 'cms_page',)}

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkpluginbase.js')

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('button_content', ''))

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if 'model' in link and 'pk' in link:
            if not hasattr(obj, '_link_model'):
                Model = get_model(*link['model'].split('.'))
                try:
                    obj._link_model = Model.objects.get(pk=link['pk'])
                except Model.DoesNotExist:
                    obj._link_model = None
            if obj._link_model:
                return obj._link_model.get_absolute_url()

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/proceed-button.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/proceed-button.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopProceedButton)


class ShopPurchaseButton(ShopPluginBase):
    """
    This button is used as a final step to convert the Cart object into an Order object.
    """
    name = _("Purchase Button")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    glossary_fields = (
        PartialFormField('button_content',
            widgets.Input(),
            label=_('Content'),
            help_text=_("Purchase buttons content")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('button_content', ''))

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/purchase-button.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/purchase-button.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopPurchaseButton)


class CheckoutDialogPlugin(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to the checkout page(s).
    Registered Cascade plugins derived from this class, require a form class in
    `settings.SHOP_CHECKOUT_FORMS` named exactly as this plugin class without the
    postfix `...Plugin`.
    """
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    CHOICES = (('form', _("Form dialog")), ('summary', _("Summary")),)
    glossary_fields = (
        PartialFormField('render_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Render as"),
            initial='form',
            help_text=_("A dialog can also be rendered as a box containing a read-only summary."),
        ),
    )

    @classmethod
    def register_plugin(cls, plugin):
        """
        Register plugins derived from this class with this function instead of
        `plugin_pool.register_plugin`, so that dialog plugins without a corresponding
        form class are not registered.
        """
        if not issubclass(plugin, cls):
            msg = "Can not register plugin class `{}`, since is does not inherit from `{}`.".format(plugin.__name__, cls.__name__)
            raise ImproperlyConfigured(msg)
        for form_class in shop_settings.CHECKOUT_FORMS:
            class_name = form_class.rsplit('.', 1)[1]
            if '{}Plugin'.format(class_name) == plugin.__name__:
                plugin_pool.register_plugin(plugin)
                break

    def __init__(self, *args, **kwargs):
        super(CheckoutDialogPlugin, self).__init__(*args, **kwargs)
        # search for the corresponding form class
        for form_class in shop_settings.CHECKOUT_FORMS:
            class_name = form_class.rsplit('.', 1)[1]
            if '{}Plugin'.format(class_name) == self.__class__.__name__:
                self.FormClass = import_by_path(form_class)
                break
        else:
            msg = "No corresponding form class could be found for plugin `{}`".format(self.__class__.__name__)
            raise ImproperlyConfigured(msg)

    def get_form_data(self, request):
        """
        Returns data to initialize the corresponding dialog form.
        This method must return a dictionary containing either `instance` - an object to initialize
        the form class for this plugin, or `initial` - a dict containing initial form data.
        """
        return {}

    def render(self, context, instance, placeholder):
        form_data = self.get_form_data(context['request'])
        context[self.FormClass.identifier] = self.FormClass(**form_data)
        return super(CheckoutDialogPlugin, self).render(context, instance, placeholder)


class CustomerFormPlugin(CheckoutDialogPlugin):
    """
    provides the form to edit customer specific data stored in model `Customer`.
    """
    name = _("Customer Form")
    cache = False

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/customer.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/customer.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        return {'instance': get_customer(request)}

CheckoutDialogPlugin.register_plugin(CustomerFormPlugin)


class CheckoutAddressPluginBase(CheckoutDialogPlugin):
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

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/shipping-address.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/shipping-address.html',
        ]
        return select_template(template_names)

CheckoutDialogPlugin.register_plugin(ShippingAddressFormPlugin)


class InvoiceAddressFormPlugin(CheckoutAddressPluginBase):
    name = _("Invoice Address Dialog")

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/invoice-address.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/invoice-address.html',
        ]
        return select_template(template_names)

CheckoutDialogPlugin.register_plugin(InvoiceAddressFormPlugin)


class PaymentMethodFormPlugin(CheckoutDialogPlugin):
    name = _("Payment Method Dialog")

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/payment-method.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/payment-method.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.payment_method}

if cart_modifiers_pool.get_payment_choices():
    # Plugin is registered only if at least one payment modifier exists
    CheckoutDialogPlugin.register_plugin(PaymentMethodFormPlugin)


class ShippingMethodFormPlugin(CheckoutDialogPlugin):
    name = _("Shipping Method Dialog")

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/shipping-method.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/shipping-method.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.shipping_method}

if cart_modifiers_pool.get_shipping_choices():
    # Plugin is registered only if at least one shipping modifier exists
    CheckoutDialogPlugin.register_plugin(ShippingMethodFormPlugin)


class ExtrasFormPlugin(CheckoutDialogPlugin):
    name = _("Extras Dialog")

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/extras.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/extras.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        cart = CartModel.objects.get_from_request(request)
        return {'initial': cart.extras or {}}

CheckoutDialogPlugin.register_plugin(ExtrasFormPlugin)
