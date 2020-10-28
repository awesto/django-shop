from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from rest_framework import serializers
from shop.conf import app_settings


class SerializeFormAsTextField(serializers.SerializerMethodField):
    def __init__(self, form_class_name, **kwargs):
        try:
            self.form_class = import_string(app_settings.SHOP_CASCADE_FORMS[form_class_name])
        except ImportError:
            msg = "Can not import Form class. Please check your settings directive SHOP_CASCADE_FORMS['{}']."
            raise ImproperlyConfigured(msg.format(form_class_name))
        super().__init__(**kwargs)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        try:
            return method(self.form_class, value)
        except AttributeError:
            return


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer to digest a summary of data required for the checkout.
    """
    customer_tag = SerializeFormAsTextField('CustomerForm')
    shipping_address_tag = SerializeFormAsTextField('ShippingAddressForm')
    billing_address_tag = SerializeFormAsTextField('BillingAddressForm')
    shipping_method_tag = SerializeFormAsTextField('ShippingMethodForm')
    payment_method_tag = SerializeFormAsTextField('PaymentMethodForm')
    extra_annotation_tag = SerializeFormAsTextField('ExtraAnnotationForm')

    def get_customer_tag(self, form_class, cart):
        form = form_class(instance=cart.customer)
        return form.as_text()

    def get_shipping_address_tag(self, form_class, cart):
        form = form_class(instance=cart.shipping_address, cart=cart)
        return form.as_text()

    def get_billing_address_tag(self, form_class, cart):
        form = form_class(instance=cart.billing_address, cart=cart)
        return form.as_text()

    def get_shipping_method_tag(self, form_class, cart):
        form = form_class(initial=cart.extra, cart=cart)
        return form.as_text()

    def get_payment_method_tag(self, form_class, cart):
        form = form_class(initial=cart.extra, cart=cart)
        return form.as_text()

    def get_extra_annotation_tag(self, form_class, cart):
        form = form_class(initial=cart.extra, cart=cart)
        return form.as_text()
