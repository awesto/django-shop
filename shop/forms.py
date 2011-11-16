#-*- coding: utf-8 -*-
from django import forms
from shop.backends_pool import backends_pool

def get_shipping_backends_choices():
    shipping_backends = backends_pool.get_shipping_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in shipping_backends])

def get_billing_backends_choices():
    billing_backends = backends_pool.get_payment_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in billing_backends])

class BillingShippingForm(forms.Form):
    """
    A form displaying all available payment and shipping methods (the ones defined
    in settings.SHOP_SHIPPING_BACKENDS and settings.SHOP_PAYMENT_BACKENDS)
    """
    shipping_method = forms.ChoiceField(choices=get_shipping_backends_choices())
    payment_method = forms.ChoiceField(choices=get_billing_backends_choices())


class CartDetailsForm(forms.Form):
    """A dynamically generated form displaying all items in the cart."""

    field_prefix = 'update_item'

    def __init__(self, cart, *args, **kwargs):
        """Instanciates the form and creates fields for each cart item."""
        super(CartDetailsForm, self).__init__(*args, **kwargs)
        self.cart = cart
        for item in cart.get_updated_cart_items():
            field_name = '%s_%d' % (self.field_prefix, item.id)
            field = forms.IntegerField(label=item.product.name, min_value=0,
                    initial=item.quantity)
            field.cart_item = item
            self.fields[field_name] = field

    def save(self):
        """Updates the quantities of the cart items."""
        cleaned_data = self.cleaned_data
        for key in cleaned_data:
            cart_item_id = int(key[len(self.field_prefix)+1:])
            self.cart.update_quantity(cart_item_id, cleaned_data[key])
