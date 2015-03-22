# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.forms import fields
from django.forms import widgets
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3ModelForm
from djangular.styling.bootstrap3.widgets import RadioSelect, RadioFieldRenderer
from shop.models.address import AddressModel
from shop.modifiers.pool import cart_modifiers_pool


class CustomerForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    identifier = 'customer'
    scope_prefix = 'data.customer'
    form_name = 'customer_form'

    class Meta:
        model = get_user_model()
        exclude = ('username', 'password', 'last_login', 'is_superuser', 'is_staff', 'is_active',
            'groups', 'user_permissions', 'date_joined',)

    @classmethod
    def update_model(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.user)
        if customer_form.is_valid():
            customer_form.save()
        else:
            return {cls.form_name: customer_form.errors}


class AddressForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    field_css_classes = {
        '*': getattr(Bootstrap3ModelForm, 'field_css_classes'),
        'zip_code': ['form-group', 'frmgrp-zip_code'],
        'location': ['form-group', 'frmgrp-location'],
    }

    priority = fields.IntegerField(widget=widgets.HiddenInput())  # TODO: use a choice field for selection

    class Meta:
        model = AddressModel
        exclude = ('user', 'priority_shipping', 'priority_invoice',)
        widgets = {
            'country': widgets.Select(attrs={'ng-change': 'update()'}),
        }

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if instance:
            initial = initial or {}
            initial['priority'] = getattr(instance, self.priority_field)
        super(AddressForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    @classmethod
    def get_model(cls):
        return cls.Meta.model

    @classmethod
    def update_model(cls, request, data, cart):
        """
        From the given request, update the database model.
        If the form data is invalid, return an error dictionary to update the response.
        """
        # search for the associated address DB instance or create a new one
        priority = data.get('priority')
        filter_args = {'user': request.user, cls.priority_field: priority}
        instance = cls.get_model().objects.filter(**filter_args).first()
        address_form = cls(data=data, instance=instance)
        if address_form.is_valid():
            if not instance:
                instance = address_form.save(commit=False)
                instance.user = request.user
                setattr(instance, cls.priority_field, priority)
            assert address_form.instance == instance
            instance.save()
            setattr(cart, cls.identifier, instance)
        else:
            return {address_form.form_name: dict(address_form.errors)}


class ShippingAddressForm(AddressForm):
    identifier = 'shipping_address'
    scope_prefix = 'data.shipping_address'
    form_name = 'shipping_addr_form'
    priority_field = 'priority_shipping'


class InvoiceAddressForm(AddressForm):
    identifier = 'invoice_address'
    scope_prefix = 'data.invoice_address'
    form_name = 'invoice_addr_form'
    priority_field = 'priority_invoice'


class PaymentMethodForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    identifier = 'payment_method'
    scope_prefix = 'data.payment_method'
    form_name = 'payment_method_form'

    payment_method = fields.ChoiceField(choices=cart_modifiers_pool.get_payment_choices(),
        widget=RadioSelect(renderer=RadioFieldRenderer, attrs={'ng-change': 'update()'}))

    @classmethod
    def update_model(cls, request, data, cart):
        cart.payment_method = data


class ShippingMethodForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    identifier = 'shipping_method'
    scope_prefix = 'data.shipping_method'
    form_name = 'shipping_method_form'

    shipping_method = fields.ChoiceField(choices=cart_modifiers_pool.get_shipping_choices(),
        widget=RadioSelect(renderer=RadioFieldRenderer, attrs={'ng-change': 'update()'}))

    @classmethod
    def update_model(cls, request, data, cart):
        cart.shipping_method = data


class AnnotationForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    identifier = 'annotation'
    scope_prefix = 'data.annotation'
    form_name = 'annotation_form'

    annotation = fields.CharField(required=False, widget=widgets.Textarea)

    @classmethod
    def update_model(cls, request, data, cart):
        cart.annotation = data.get('annotation')
