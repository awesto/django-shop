# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.forms import widgets
from django.forms.utils import ErrorDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from djng.forms import fields
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm

from shop.models.address import ShippingAddressModel, BillingAddressModel
from shop.models.customer import CustomerModel
from shop.modifiers.pool import cart_modifiers_pool
from .base import DialogForm, DialogModelForm, UniqueEmailValidationMixin


class CustomerForm(DialogModelForm):
    scope_prefix = 'data.customer'
    legend = _("Customer's Details")

    email = fields.EmailField(label=_("Email address"))
    first_name = fields.CharField(label=_("First Name"))
    last_name = fields.CharField(label=_("Last Name"))

    class Meta:
        model = CustomerModel
        exclude = ['user', 'recognized', 'number', 'last_access']
        custom_fields = ['email', 'first_name', 'last_name']

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        initial = dict(initial) if initial else {}
        assert instance is not None
        initial.update(dict((f, getattr(instance, f)) for f in self.Meta.custom_fields))
        super(CustomerForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    def save(self, commit=True):
        for f in self.Meta.custom_fields:
            setattr(self.instance, f, self.cleaned_data[f])
        return super(CustomerForm, self).save(commit)

    @classmethod
    def form_factory(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.customer)
        if customer_form.is_valid():
            customer_form.instance.recognize_as_registered(request, commit=False)
            customer_form.save()
        return customer_form


class GuestForm(UniqueEmailValidationMixin, DialogModelForm):
    scope_prefix = 'data.guest'
    form_name = 'customer_form'  # Override form name to reuse template `customer-form.html`
    legend = _("Customer's Email")

    email = fields.EmailField(label=_("Email address"))

    class Meta:
        model = get_user_model()  # since we only use the email field, use the User model directly
        fields = ['email']

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if isinstance(instance, CustomerModel):
            instance = instance.user
        super(GuestForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.customer.user)
        if customer_form.is_valid():
            request.customer.recognize_as_guest(request, commit=False)
            customer_form.save()
        return customer_form


class AddressForm(DialogModelForm):
    # field to be superseeded by a select widget
    active_priority = fields.CharField(
        required=False,
        widget=widgets.HiddenInput(),
    )

    use_primary_address = fields.BooleanField(
        label="use primary address",  # label will be overridden by Shipping/Billing/AddressForm
        required=False,
        initial=True,
        widget=widgets.CheckboxInput(),
    )

    # JS function to filter form_entities after removing an entity
    js_filter = "var list = [].slice.call(arguments); return list.filter(function(a) {{ return a.value != '{}'; }});"
    plugin_fields = ['plugin_id', 'plugin_order', 'use_primary_address']

    class Meta:
        exclude = ('customer', 'priority',)

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        self.multi_addr = kwargs.pop('multi_addr', False)
        self.allow_use_primary = kwargs.pop('allow_use_primary', False)
        self.form_entities = kwargs.pop('form_entities', [])
        if instance:
            cart = kwargs['cart']
            initial = dict(initial or {}, active_priority=instance.priority)
            if instance.address_type == 'shipping':
                initial['use_primary_address'] = cart.shipping_address is None
            else:  # address_type == billing
                initial['use_primary_address'] = cart.billing_address is None
        super(AddressForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    @classmethod
    def get_model(cls):
        return cls.Meta.model

    @cached_property
    def field_css_classes(self):
        css_classes = {'*': getattr(Bootstrap3ModelForm, 'field_css_classes')}
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                css_classes[name] = ['has-feedback', 'form-group', 'shop-address-{}'.format(name)]
        return css_classes

    @classmethod
    def form_factory(cls, request, data, cart):
        """
        From the given request, update the database model.
        If the form data is invalid, return an error dictionary to update the response.
        """
        # search for the associated address DB instance or create a new one
        current_address = cls.get_address(cart)
        try:
            active_priority = int(data.get('active_priority'))
        except (ValueError, TypeError):
            if data.get('use_primary_address'):
                active_priority = 'nop'
            else:
                active_priority = data.get('active_priority', 'new')
            active_address = cls.get_model().objects.get_fallback(customer=request.customer)
        else:
            filter_args = dict(customer=request.customer, priority=active_priority)
            active_address = cls.get_model().objects.filter(**filter_args).first()

        if data.pop('remove_entity', False):
            if active_address and (isinstance(active_priority, int) or data.get('is_pending')):
                active_address.delete()
            old_address = cls.get_model().objects.get_fallback(customer=request.customer)
            if old_address:
                faked_data = dict(data)
                faked_data.update(
                    dict((field.name, old_address.serializable_value(field.name))
                         for field in old_address._meta.fields))
                address_form = cls(data=faked_data)
                remove_entity_filter = cls.js_filter.format(active_priority)
                address_form.data.update(
                    active_priority=str(old_address.priority),
                    remove_entity_filter=mark_safe(remove_entity_filter),
                )
            else:
                address_form = cls()
                address_form.data.update(
                    active_priority='add',
                    plugin_id=data.get('plugin_id'),
                    plugin_order=data.get('plugin_order'),
                )
            address_form.set_address(cart, old_address)
        elif active_priority == 'add':
            # Add a newly filled address for the given customer
            address_form = cls(data=data, cart=cart)
            if address_form.is_valid():
                # prevent adding the same address twice
                all_field_names = [f.name for f in cls.get_model()._meta.get_fields()]
                filter_args = dict((attr, val) for attr, val in address_form.data.items()
                                   if attr in all_field_names and val)
                filter_args.update(customer=request.customer)
                try:
                    existing_address = cls.get_model().objects.get(**filter_args)
                except cls.get_model().DoesNotExist:
                    next_address = address_form.save(commit=False)
                    if next_address:
                        next_address.customer = request.customer
                        next_address.priority = cls.get_model().objects.get_max_priority(request.customer) + 1
                        next_address.save()
                        address_form.data.update(active_priority=str(next_address.priority))
                    else:
                        address_form.data.update(active_priority='nop')
                    address_form.set_address(cart, next_address)
                else:
                    address_form.set_address(cart, existing_address)
        elif active_priority == 'new' or active_address is None and not data.get('use_primary_address'):
            # customer selected 'Add another address', hence create a new empty form
            initial = dict((key, val) for key, val in data.items() if key in cls.plugin_fields)
            address_form = cls(initial=initial)
            address_form.data.update(address_form.get_initial_data())
            address_form.data.update(active_priority='add')
        elif current_address == active_address:
            # an existing entity of AddressModel was edited
            address_form = cls(data=data, instance=active_address, cart=cart)
            if address_form.is_valid():
                next_address = address_form.save()
                address_form.set_address(cart, next_address)
        else:
            # an address with another priority was selected
            initial = dict(data)
            for attr in cls().get_initial_data().keys():
                if hasattr(active_address, attr):
                    initial.update({attr: getattr(active_address, attr)})
            initial.update(active_priority=str(active_address.priority))
            address_form = cls(data=initial, instance=current_address, cart=cart)
            address_form.set_address(cart, active_address)
        return address_form

    def get_response_data(self):
        return self.data

    def full_clean(self):
        super(AddressForm, self).full_clean()
        if self.is_bound and self['use_primary_address'].value():
            # reset errors, since then the form is always regarded as valid
            self._errors = ErrorDict()

    def save(self, commit=True):
        if not self['use_primary_address'].value():
            return super(AddressForm, self).save(commit)

    def as_div(self):
        # Intentionally rendered without field `use_primary_address`, this must be added
        # on top of the form template manually
        self.fields.pop('use_primary_address', None)
        return super(AddressForm, self).as_div()

    def as_text(self):
        bound_field = self['use_primary_address']
        if bound_field.value():
            return bound_field.field.widget.choice_label
        return super(AddressForm, self).as_text()


class ShippingAddressForm(AddressForm):
    scope_prefix = 'data.shipping_address'
    legend = _("Shipping Address")

    class Meta(AddressForm.Meta):
        model = ShippingAddressModel
        widgets = {
            'country': widgets.Select(attrs={'ng-change': 'updateCountry()'}),
        }

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        primary_address_widget = self.fields['use_primary_address'].widget
        primary_address_widget.choice_label = _("Use billing address for shipping")

    @classmethod
    def get_address(cls, cart):
        return cart.shipping_address

    def set_address(self, cart, instance):
        cart.shipping_address = instance if not self['use_primary_address'].value() else None


class BillingAddressForm(AddressForm):
    scope_prefix = 'data.billing_address'
    legend = _("Billing Address")

    class Meta(AddressForm.Meta):
        model = BillingAddressModel

    def __init__(self, *args, **kwargs):
        super(BillingAddressForm, self).__init__(*args, **kwargs)
        primary_address_widget = self.fields['use_primary_address'].widget
        primary_address_widget.choice_label = _("Use shipping address for billing")

    @classmethod
    def get_address(cls, cart):
        return cart.billing_address

    def set_address(self, cart, instance):
        cart.billing_address = instance if not self['use_primary_address'].value() else None


class PaymentMethodForm(DialogForm):
    scope_prefix = 'data.payment_method'

    payment_modifier = fields.ChoiceField(
        label=_("Payment Method"),
        widget=widgets.RadioSelect(attrs={'ng-change': 'upload()'}),
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

    def has_choices(self):
        return len(self.base_fields['payment_modifier'].choices) > 0

    @classmethod
    def form_factory(cls, request, data, cart):
        cart.update(request)
        payment_method_form = cls(data=data, cart=cart)
        if payment_method_form.is_valid():
            cart.extra.update(payment_method_form.cleaned_data,
                payment_extra_data=data.get('payment_data', {}))
        return payment_method_form


class ShippingMethodForm(DialogForm):
    scope_prefix = 'data.shipping_method'

    shipping_modifier = fields.ChoiceField(
        label=_("Shipping Method"),
        widget=widgets.RadioSelect(attrs={'ng-change': 'upload()'}),
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

    def has_choices(self):
        return len(self.base_fields['shipping_modifier'].choices) > 0

    @classmethod
    def form_factory(cls, request, data, cart):
        cart.update(request)
        shipping_method_form = cls(data=data, cart=cart)
        if shipping_method_form.is_valid():
            cart.extra.update(shipping_method_form.cleaned_data)
        return shipping_method_form


class ExtraAnnotationForm(DialogForm):
    scope_prefix = 'data.extra_annotation'

    annotation = fields.CharField(
        label=_("Extra annotation for this order"),
        required=False,
        widget=widgets.Textarea,
    )

    @classmethod
    def form_factory(cls, request, data, cart):
        extra_annotation_form = cls(data=data)
        if extra_annotation_form.is_valid():
            cart.extra.update(extra_annotation_form.cleaned_data)
        return extra_annotation_form


class AcceptConditionForm(DialogForm):
    scope_prefix = 'data.accept_condition'

    accept = fields.BooleanField(
        required=True,
        widget=widgets.CheckboxInput(),
    )

    def __init__(self, data=None, initial=None, *args, **kwargs):
        plugin_id = data and data.get('plugin_id') or initial and initial.get('plugin_id') or 'none'
        scope_prefix = '{0}.plugin_{1}'.format(self.scope_prefix, plugin_id)
        self.form_name = '{0}.plugin_{1}'.format(self.form_name, plugin_id)
        super(AcceptConditionForm, self).__init__(data=data, initial=initial,
                                                  scope_prefix=scope_prefix, *args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        data = data or {'accept': False}
        accept_form = cls(data=data)
        return accept_form
