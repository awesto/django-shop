# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.forms import fields, widgets
from django.forms.utils import ErrorDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm
from djng.styling.bootstrap3.widgets import RadioSelect, RadioFieldRenderer, CheckboxInput
from shop.models.address import AddressModel
from shop.models.customer import CustomerModel
from shop.modifiers.pool import cart_modifiers_pool
from .base import DialogForm, DialogModelForm


class CustomerForm(DialogModelForm):
    scope_prefix = 'data.customer'
    legend = _("Customer Details")

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
        return customer_form


class GuestForm(DialogModelForm):
    scope_prefix = 'data.guest'
    form_name = 'customer_form'  # Override form name to reuse template `customer-form.html`
    legend = _("Customer Details")

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
        return customer_form

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

    active_priority = fields.CharField(required=False, widget=widgets.HiddenInput())

    # JS function to filter form_entities after removing an entity
    js_filter = 'var list = [].slice.call(arguments); return list.filter(function(a) {{ return a.value != {}; }});'

    class Meta:
        model = AddressModel
        exclude = ('customer', 'priority_shipping', 'priority_billing',)

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        self.multi_addr = kwargs.pop('multi_addr', False)
        self.form_entities = kwargs.pop('form_entities', [])
        if instance:
            initial = initial or {}
            initial['active_priority'] = getattr(instance, self.priority_field)
        super(AddressForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    def must_persist(self):
        return True

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
        current_priority = getattr(cls.get_address(cart), cls.priority_field, None)
        try:
            active_priority = int(data.get('active_priority'))
        except (TypeError, ValueError):
            active_priority = current_priority
        try:
            if active_priority:
                filter_args = {'customer': request.customer, cls.priority_field: active_priority}
                active_instance = cls.get_model().objects.get(**filter_args)
            else:
                active_instance = None
        except cls.get_model().DoesNotExist:
            active_instance = None

        if data.pop('remove_entity', False):
            if active_instance:
                active_instance.delete()
            exclude_kwargs = {cls.priority_field: None}
            instance = cls.get_model().objects.filter(customer=request.customer).exclude(**exclude_kwargs).last()
            faked_data = dict((key, getattr(instance, key, val)) for key, val in data.items())
            faked_data.update(active_priority=getattr(instance, cls.priority_field))
            address_form = cls(data=faked_data, instance=instance)
            if active_instance:
                remove_entity_filter = cls.js_filter.format(getattr(active_instance, cls.priority_field))
                address_form.data.update(remove_entity_filter=mark_safe(remove_entity_filter))
            cls.set_address(cart, instance)
        elif data.get('active_priority') == 'new' and current_priority > 0:
            # customer selected 'Add another address', hence create a new empty form
            for key in data.keys():
                if key not in ('plugin_id', 'plugin_order', 'active_priority'):
                    data[key] = ''
            address_form = cls(data=data)
            address_form.data.update(active_priority='add')
            cls.set_address(cart, None)
        elif current_priority == active_priority:
            # an existing entity of AddressModel was edited
            address_form = cls(data=data, instance=active_instance)
            if address_form.is_valid() and address_form.must_persist():
                instance = address_form.save(commit=False)
                if active_instance is None:
                    # add address as new entity
                    instance.customer = request.customer
                    next_priority = cls.get_max_priority(request.customer) + 1
                    setattr(instance, cls.priority_field, next_priority)
                instance.save()
                cls.set_address(cart, instance)
        else:
            # an address with another priority was selected
            faked_data = dict((key, getattr(active_instance, key, val)) for key, val in data.items())
            address_form = cls(data=faked_data, instance=active_instance)
            cls.set_address(cart, active_instance)

        return address_form

    @classmethod
    def get_max_priority(cls, customer):
        """
        Return the maximum priority for this address model.
        """
        aggr = cls.get_model().objects.filter(customer=customer).aggregate(Max(cls.priority_field))
        return aggr['{}__max'.format(cls.priority_field)] or 0

    def get_response_data(self):
        return self.data


class ShippingAddressForm(AddressForm):
    scope_prefix = 'data.shipping_address'
    priority_field = 'priority_shipping'
    legend = _("Shipping Address")

    class Meta(AddressForm.Meta):
        widgets = {
            'country': widgets.Select(attrs={'ng-change': 'upload()'}),
        }

    @classmethod
    def get_address(cls, cart):
        return cart.shipping_address

    @classmethod
    def set_address(cls, cart, instance):
        cart.shipping_address = instance


class BillingAddressForm(AddressForm):
    scope_prefix = 'data.billing_address'
    priority_field = 'priority_billing'
    legend = _("Billing Address")

    use_shipping_address = fields.BooleanField(required=False, initial=True,
        widget=CheckboxInput(_("Use shipping address for billing"),
            attrs={'ng-change': 'switchEntity(billing_address_form)'}))

    @classmethod
    def get_address(cls, cart):
        return cart.billing_address

    @classmethod
    def set_address(cls, cart, instance):
        if getattr(instance, 'use_shipping_address', False):
            cart.billing_address = cart.shipping_address
        else:
            cart.billing_address = instance

    def full_clean(self):
        super(BillingAddressForm, self).full_clean()
        if 'use_shipping_address' in self and self['use_shipping_address'].value():
            # reset errors, since then the form is always regarded as valid
            self._errors = ErrorDict()
            self.instance.use_shipping_address = True
        else:
            self.instance.use_shipping_address = False

    def must_persist(self):
        return not self['use_shipping_address'].value()

    def as_div(self):
        # Intentionally rendered without field `use_shipping_address`
        self.fields.pop('use_shipping_address', None)
        return super(BillingAddressForm, self).as_div()

    def as_text(self):
        try:
            bound_field = self['use_shipping_address']
            if bound_field.value():
                return bound_field.field.widget.choice_label
        except KeyError:
            return super(BillingAddressForm, self).as_text()


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
            cart.extra.update(payment_method_form.cleaned_data,
                payment_extra_data=data.get('payment_data', {}))
        return payment_method_form


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
        return shipping_method_form


class ExtraAnnotationForm(DialogForm):
    scope_prefix = 'data.extra_annotation'

    annotation = fields.CharField(label=_("Extra annotation for this order"), required=False,
                                  widget=widgets.Textarea)

    @classmethod
    def form_factory(cls, request, data, cart):
        extra_annotation_form = cls(data=data)
        if extra_annotation_form.is_valid():
            cart.extra.update(extra_annotation_form.cleaned_data)
        return extra_annotation_form


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
        return accept_form
