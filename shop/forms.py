from django import forms
from shop.models.clientmodel import *

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        widgets = {
            'is_shipping':forms.HiddenInput(),
            'is_billing':forms.HiddenInput(),
            'client':forms.HiddenInput(),
        }
