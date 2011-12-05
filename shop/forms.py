#-*- coding: utf-8 -*-
"""Forms for the django-shop app."""
from django import forms
from django.forms.models import modelformset_factory

from shop.backends_pool import backends_pool
from shop.models.cartmodel import CartItem


def get_shipping_backends_choices():
    shipping_backends = backends_pool.get_shipping_backends_list()
    return tuple(
        [(x.url_namespace, x.backend_name) for x in shipping_backends])


def get_billing_backends_choices():
    billing_backends = backends_pool.get_payment_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in billing_backends])


class BillingShippingForm(forms.Form):
    """
    A form displaying all available payment and shipping methods (the ones
    defined in settings.SHOP_SHIPPING_BACKENDS and
    settings.SHOP_PAYMENT_BACKENDS)
    """
    shipping_method = forms.ChoiceField(
        choices=get_shipping_backends_choices())
    payment_method = forms.ChoiceField(choices=get_billing_backends_choices())


class CartItemModelForm(forms.ModelForm):
    """A form for the CartItem model. To be used in the CartDetails view."""

    quantity = forms.IntegerField(min_value=0, max_value=9999)

    class Meta:
        model = CartItem
        fields = ('quantity', )

    def save(self, *args, **kwargs):
        """
        We don't save the model using the regular way here because the
        Cart's ``update_quantity()`` method already takes care of deleting
        items from the cart when the quantity is set to 0.
        """
        quantity = self.cleaned_data['quantity']
        instance = self.instance.cart.update_quantity(self.instance.id,
                quantity)
        return instance


def get_cart_item_formset(cart_items=None, data=None):
    """
    Returns a CartItemFormSet which can be used in the CartDetails view.

    :param cart_items: The queryset to be used for this formset. This should
      be the list of updated cart items of the current cart.
    :param data: Optional POST data to be bound to this formset.
    """
    assert(cart_items is not None)
    CartItemFormSet = modelformset_factory(CartItem, form=CartItemModelForm,
            extra=0)
    kwargs = {'queryset': cart_items, }
    form_set = CartItemFormSet(data, **kwargs)

    # The Django ModelFormSet pulls the item out of the database again and we
    # would lose the updated line_subtotals
    for form in form_set:
        for cart_item in cart_items:
            if form.instance.id == cart_item.id:
                form.instance = cart_item
    return form_set
