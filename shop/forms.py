#-*- coding: utf-8 -*-
"""Forms for the django-shop app."""
from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList, ErrorDict
from django.utils.translation import ugettext_lazy as _

from shop.models.cartmodel import CartItem
from shop.models import PaymentBackend, ShippingBackend
from shop.util.loader import load_class


class BillingShippingForm(forms.Form):
    """
    A form displaying all available payment and shipping methods 
    """
    shipping_backend = forms.ModelChoiceField(
        queryset=ShippingBackend.objects.filter(active=True),
        empty_label=None, label=_('Shipping method'))
    payment_backend = forms.ModelChoiceField(
        queryset=PaymentBackend.objects.filter(active=True),
        empty_label=None, label=_('Payment method'))


class AddressesForm(forms.Form):
    '''Uberform which manages shipping and billing addresses. It provides the
    option for the addresses to be the same.

    You can pass `billing` (resp. `shipping`) models instances to edit them.
    You can pass your own `billing_form_class` and `shipping_form_class` which
    have to be `ModelForm` subclasses. This form also supports `empty_permitted`.
    The form takes optional keyword `required`. If it's True, then validation 
    will fail if neither address is filled in.
    
    This form contains one own field - `addresses_the_same` and two subforms -
    `billing`, `shipping`
    '''

    addresses_the_same = forms.BooleanField(label=_("Shipping is the same as billing"), required=False)

    def __init__(self, data=None, files=None, billing=None, shipping=None,
                 billing_form_class=None, shipping_form_class=None,
                 auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False):

        bform = (billing_form_class or AddressForm)
        sform = (shipping_form_class or AddressForm)

        self.billing = bform(data, files, instance=billing, prefix="billing",
                             initial=initial.pop("billing", None), label_suffix=label_suffix)

        self.shipping = sform(data, files, prefix="shipping",
                              instance=shipping if shipping != billing else None,
                              initial=initial.pop("shipping", None), label_suffix=label_suffix)

        super(AddressesForm, self).__init__(data, files,
                                            initial={"addresses_the_same": (shipping == billing)},
                                            label_suffix=label_suffix)

    def clean(self):
        '''The form is valid even when both addresses are empty'''
        data = self.cleaned_data
        if not data.get('addresses_the_same', True):
            # both has to be valid
            if not (self.shipping.is_valid() and billing.is_valid()):  # shipping has to be filled in
                raise ValidationError(_('Shipping address has to be filled when marked different'))

        if not self.billing.is_valid():
            if not self.empty_permitted:
                raise ValidationError(_('An address is required'))
            self.billing_empty = True

            # if there is some data in billing then it was not intended to be empty
            if self.billing.cleaned_data.get("street"):
                self.shipping._errors = ErrorDict()
                raise ValidationError()

        # in all other cases are valid
        self.billing._errors = ErrorDict()
        self.shipping._errors = ErrorDict()

        data['billing'] = getattr(self.billing, "cleaned_data", {})
        data['shipping'] = getattr(self.shipping, "cleaned_data", {})

        return data

    def save(self, commit=True):
        '''This method returns tuple with address models.
        In the case when empty form was allowed (`required=False` in the constructor)
        tuple `(None, None)` might be returned.'''
        billing = None
        shipping = None

        if not self.billing_empty:
            billing = self.billing.save(commit=commit)

        if self.cleaned_data['addresses_the_same']:
            shipping = billing
        else:
            shipping = self.shipping.save(commit=commit)
        return (billing, shipping)

    def save_to_request(self, request):
        if request.user.is_authenticated():
            billing, shipping = self.save(commit=False)
            if shipping:
                shipping.user_shipping = request.user
                if not shipping.name:
                    shipping.name = request.user.get_full_name()
                if shipping != billing:
                    # reset billing address because it could have changed
                    shipping.user_billing = None
                shipping.save()
            if billing:
                billing.user_billing = request.user
                if not billing.name:
                    billing.name = request.user.get_full_name()
                billing.save()
        else:
            billing, shipping = self.save(commit=True)
            if shipping:
                request.session['shipping_address_id'] = shipping.pk
            if billing:
                request.session['billing_address_id'] = billing.pk
        return billing, shipping


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
        instance = self.instance.cart.update_quantity(self.instance.pk,
                quantity)
        return instance


def get_cart_item_modelform_class():
    """
    Return the class of the CartItem ModelForm.

    The default `shop.forms.CartItemModelForm` can be overridden settings
    ``SHOP_CART_ITEM_FORM`` parameter in settings
    """
    cls_name = getattr(settings, 'SHOP_CART_ITEM_FORM', 'shop.forms.CartItemModelForm')
    cls = load_class(cls_name)
    return cls


def get_cart_item_formset(cart_items=None, data=None):
    """
    Returns a CartItemFormSet which can be used in the CartDetails view.

    :param cart_items: The queryset to be used for this formset. This should
      be the list of updated cart items of the current cart.
    :param data: Optional POST data to be bound to this formset.
    """
    assert(cart_items is not None)
    CartItemFormSet = modelformset_factory(CartItem, form=get_cart_item_modelform_class(),
            extra=0)
    kwargs = {'queryset': cart_items, }
    form_set = CartItemFormSet(data, **kwargs)

    # The Django ModelFormSet pulls the item out of the database again and we
    # would lose the updated line_subtotals
    for form in form_set:
        for cart_item in cart_items:
            if form.instance.pk == cart_item.pk:
                form.instance = cart_item
    return form_set
