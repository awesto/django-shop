# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.forms import fields, widgets
from django.utils.translation import ugettext_lazy as _
from djangular.styling.bootstrap3.forms import Bootstrap3ModelForm
from djangular.styling.bootstrap3.widgets import RadioSelect, RadioFieldRenderer, CheckboxInput
from shop.models.address import AddressModel
from shop.models.customer import CustomerModel
from shop.modifiers.pool import cart_modifiers_pool
from .base import DialogForm, DialogModelForm


class CustomerForm(DialogModelForm):
    scope_prefix = 'data.customer'
    email = fields.EmailField(label=_("Email address"))
    first_name = fields.CharField(label=_("First Name"))
    last_name = fields.CharField(label=_("Last Name"))

    class Meta:
        model = CustomerModel
        exclude = ('user', 'recognized', 'number', 'last_access',)
        custom_fields = ('email', 'first_name', 'last_name',)

    def __init__(self, initial={}, instance=None, *args, **kwargs):
        assert instance is not None and isinstance(initial, dict)
        initial.update(dict((f, getattr(instance, f)) for f in self.Meta.custom_fields))
        super(CustomerForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    def save(self, commit=True):
        self.instance.recognize_as_registered()
        for f in self.Meta.custom_fields:
            setattr(self.instance, f, self.cleaned_data[f])
        return super(CustomerForm, self).save(commit)

    @classmethod
    def form_factory(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.customer)
        if customer_form.is_valid():
            customer_form.save()
        else:
            return {cls.form_name: customer_form.errors}


class GuestForm(DialogModelForm):
    scope_prefix = 'data.guest'
    form_name = 'customer_form'  # Override form name to reuse template `customer.html`

    email = fields.EmailField(label=_("Email address"))

    class Meta:
        model = get_user_model()  # since we only use the email field, use the User model directly
        fields = ('email',)

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if isinstance(instance, CustomerModel._materialized_model):
            instance = instance.user
        super(GuestForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.customer.user)
        if customer_form.is_valid():
            customer_form.save()
        else:
            return {cls.form_name: customer_form.errors}

    def clean_email(self):
        # check for uniqueness of email address
        if get_user_model().objects.filter(is_active=True, email=self.cleaned_data['email']).exists():
            msg = _("A registered customer with the e-mail address ‘{email}’ already exists.\n"
                    "If you have used this address previously, try to reset the password.")
            raise ValidationError(msg.format(**self.cleaned_data))
        return self.cleaned_data['email']


class AddressForm(DialogModelForm):
    field_css_classes = {
        '*': getattr(Bootstrap3ModelForm, 'field_css_classes'),
        'zip_code': ['has-feedback', 'form-group', 'frmgrp-zip_code'],
        'location': ['has-feedback', 'form-group', 'frmgrp-location'],
        'street_name': ['has-feedback', 'form-group', 'frmgrp-street_name'],
        'street_number': ['has-feedback', 'form-group', 'frmgrp-street_number'],
    }

    priority = fields.IntegerField(widget=widgets.HiddenInput())  # TODO: use a choice field for selection

    class Meta:
        model = AddressModel
        exclude = ('customer', 'priority_shipping', 'priority_billing',)

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if instance:
            initial = initial or {}
            initial['priority'] = getattr(instance, self.priority_field)
        super(AddressForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    @classmethod
    def get_model(cls):
        return cls.Meta.model

    @classmethod
    def form_factory(cls, request, data, cart):
        """
        From the given request, update the database model.
        If the form data is invalid, return an error dictionary to update the response.
        """
        # search for the associated address DB instance or create a new one
        priority = data and data.get('priority') or 0
        filter_args = {'customer': request.customer, cls.priority_field: priority}
        instance = cls.get_model().objects.filter(**filter_args).first()
        address_form = cls(data=data, instance=instance)
        if address_form.is_valid():
            if not instance:
                instance = address_form.save(commit=False)
                instance.customer = request.customer
                setattr(instance, cls.priority_field, priority)
            assert address_form.instance == instance
            instance.save()
            cls.set_address(cart, instance)
        else:
            return {address_form.form_name: dict(address_form.errors)}

    @classmethod
    def get_max_priority(cls, customer):
        """
        Return the maximum priority for this address model.
        """
        aggr = cls.get_model().objects.filter(customer=customer).aggregate(Max(cls.priority_field))
        return aggr.get('{}__max'.format(cls.priority_field, 0))

    @classmethod
    def set_address(cls, cart, instance):
        # TODO: method must be connected to allow different priorities
        address_form = cls(instance=instance)
        data = address_form.initial
        data.pop('id', None)
        data.initial.pop('priority', None)
        data.update({'customer': cart.customer, '{}__isnull'.format(cls.priority_field): False})
        instance, created = cls.get_model().objects.get_or_create(**data)
        if created:
            instance.priority_billing = cls.get_max_priority(cart.customer) + 1
            instance.save()


class ShippingAddressForm(AddressForm):
    scope_prefix = 'data.shipping_address'
    priority_field = 'priority_shipping'

    class Meta(AddressForm.Meta):
        widgets = {
            'country': widgets.Select(attrs={'ng-change': 'upload()'}),
        }

    @classmethod
    def set_address(cls, cart, instance):
        # TODO: super(ShippingAddressForm, cls).set_address(cart, instance)
        cart.shipping_address = instance


class BillingAddressForm(AddressForm):
    scope_prefix = 'data.billing_address'
    priority_field = 'priority_billing'

    use_shipping_address = fields.BooleanField(required=False, initial=True,
        widget=CheckboxInput(_("Use shipping address for billing")))

    def as_div(self):
        # Intentionally rendered without field `use_shipping_address`
        self.fields.pop('use_shipping_address', None)
        return super(BillingAddressForm, self).as_div()

    @classmethod
    def form_factory(cls, request, data, cart):
        """
        Overridden method to reuse data from ShippingAddressForm in case the checkbox for
        `use_shipping_address` is active.
        """
        if data and data.pop('use_shipping_address', False):
            cls.set_address(cart, cart.shipping_address)
        else:
            return super(BillingAddressForm, cls).form_factory(request, data, cart)

    @classmethod
    def set_address(cls, cart, instance):
        # TODO: super(BillingAddressForm, cls).set_address(cart, instance)
        cart.billing_address = instance


class PaymentMethodForm(DialogForm):
    scope_prefix = 'data.payment_method'

    payment_modifier = fields.ChoiceField(label=_("Payment Method"),
        widget=RadioSelect(renderer=RadioFieldRenderer, attrs={'ng-change': 'upload()'})
    )

    def __init__(self, *args, **kwargs):
        choices = [m.get_choice() for m in cart_modifiers_pool.get_payment_modifiers()
                   if not m.is_disabled(kwargs['cart'])]
        self.base_fields['payment_modifier'].choices = choices
        if len(choices) == 1:
            # if there is only one shipping method available, always set it as default
            try:
                kwargs['initial']['payment_modifier'] = choices[0][0]
            except KeyError:
                pass
        super(PaymentMethodForm, self).__init__(*args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        cart.update(request)
        payment_method_form = cls(data=data, cart=cart)
        if payment_method_form.is_valid():
            cart.extra.update(payment_method_form.cleaned_data)
        else:
            return {cls.form_name: payment_method_form.errors}


class ShippingMethodForm(DialogForm):
    scope_prefix = 'data.shipping_method'

    shipping_modifier = fields.ChoiceField(label=_("Shipping Method"),
        widget=RadioSelect(renderer=RadioFieldRenderer, attrs={'ng-change': 'upload()'})
    )

    def __init__(self, *args, **kwargs):
        choices = [m.get_choice() for m in cart_modifiers_pool.get_shipping_modifiers()
                   if not m.is_disabled(kwargs['cart'])]
        self.base_fields['shipping_modifier'].choices = choices
        if len(choices) == 1:
            # with only one choice, initialize with it
            try:
                kwargs['initial']['shipping_modifier'] = choices[0][0]
            except KeyError:
                pass
        super(ShippingMethodForm, self).__init__(*args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        cart.update(request)
        shipping_method_form = cls(data=data, cart=cart)
        if shipping_method_form.is_valid():
            cart.extra.update(shipping_method_form.cleaned_data)
        else:
            return {cls.form_name: shipping_method_form.errors}


class ExtraAnnotationForm(DialogForm):
    scope_prefix = 'data.extra_annotation'

    annotation = fields.CharField(label=_("Extra annotation for this order"), required=False,
                                  widget=widgets.Textarea)

    @classmethod
    def form_factory(cls, request, data, cart):
        extra_annotation_form = cls(data=data)
        if extra_annotation_form.is_valid():
            cart.extra.update(extra_annotation_form.cleaned_data)
        else:
            return {cls.form_name: extra_annotation_form.errors}


class AcceptConditionForm(DialogForm):
    scope_prefix = 'data.accept_condition'

    accept = fields.BooleanField(required=True, widget=CheckboxInput(None))

    def __init__(self, data=None, initial=None, *args, **kwargs):
        plugin_id = data and data.get('plugin_id') or initial and initial.get('plugin_id') or 'none'
        scope_prefix = '{0}.plugin_{1}'.format(self.scope_prefix, plugin_id)
        self.form_name = '{0}.plugin_{1}'.format(self.form_name, plugin_id)
        super(AcceptConditionForm, self).__init__(data=data, initial=initial, scope_prefix=scope_prefix, *args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        data = data or {'accept': False}
        accept_form = cls(data=data)
        if not accept_form.is_valid():
            return {accept_form.form_name: dict(accept_form.errors)}
