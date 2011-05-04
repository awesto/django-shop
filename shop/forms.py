from django import forms
from shop.models.clientmodel import *
from shop.backends_pool import backends_pool

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        widgets = {
            'is_shipping':forms.HiddenInput(),
            'is_billing':forms.HiddenInput(),
            'client':forms.HiddenInput(),
        }

def _get_shipping_backends():
    shipping_backends = backends_pool.get_shipping_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in shipping_backends])
def _get_billing_backends():
    billing_backends = backends_pool.get_payment_backends_list()
    return tuple([(x.url_namespace, x.backend_name) for x in billing_backends])
class BillingShippingForm(forms.Form):
    shipping_method = forms.ChoiceField(choices=_get_shipping_backends())
    payment_method = forms.ChoiceField(choices=_get_billing_backends())
