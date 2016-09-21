# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.timezone import localtime
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from shop.models.customer import CustomerModel, CustomerState


class CustomerInlineAdmin(admin.StackedInline):
    model = CustomerModel
    fieldsets = (
        (None, {'fields': ('salutation', 'get_number')}),
        (_("Shipping Addresses"), {'fields': ('get_shipping_addresses',)})
    )
    readonly_fields = ('get_number', 'get_shipping_addresses',)

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj is None else 1

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_number(self, customer):
        return customer.get_number()
    get_number.short_description = pgettext_lazy('customer', "Number")

    def get_shipping_addresses(self, customer):
        addresses = [(a.as_text(),) for a in customer.shippingaddress_set.all()]
        return format_html_join('', '<address>{0}</address>', addresses)
    get_shipping_addresses.short_description = ''
    get_shipping_addresses.allow_tags = True


class CustomerCreationForm(UserCreationForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()

    def save(self, commit=True):
        self.instance.is_staff = True
        return super(CustomerCreationForm, self).save(commit=False)


class CustomerChangeForm(UserChangeForm):
    email = forms.EmailField(required=False)

    class Meta(UserChangeForm.Meta):
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance')
        initial['email'] = instance.email or ''
        super(CustomerChangeForm, self).__init__(initial=initial, *args, **kwargs)

    def clean_email(self):
        # nullify empty email field in order to prevent unique index collisions
        return self.cleaned_data.get('email').strip() or None

    def save(self, commit=False):
        self.instance.email = self.cleaned_data['email']
        return super(CustomerChangeForm, self).save(commit)


class CustomerListFilter(admin.SimpleListFilter):
    title = _("Customer State")
    parameter_name = 'custate'

    def lookups(self, request, model_admin):
        return CustomerState.choices()

    def queryset(self, request, queryset):
        try:
            queryset = queryset.filter(customer__recognized=CustomerState(int(self.value())))
        finally:
            return queryset


class CustomerAdmin(UserAdmin):
    """
    This ModelAdmin class must be registered inside the implementation of this shop.
    """
    form = CustomerChangeForm
    add_form = CustomerCreationForm
    inlines = (CustomerInlineAdmin,)
    list_display = ('get_username', 'salutation', 'last_name', 'first_name', 'recognized',
        'last_access', 'is_unexpired')
    segmentation_list_display = ('get_username',)
    list_filter = UserAdmin.list_filter + (CustomerListFilter,)
    readonly_fields = ('last_login', 'date_joined', 'last_access', 'recognized')
    ordering = ('id',)

    class Media:
        js = ('shop/js/admin/customer.js',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CustomerAdmin, self).get_fieldsets(request, obj=obj)
        if obj:
            fieldsets[0][1]['fields'] = ('username', 'recognized', 'password',)
            fieldsets[3][1]['fields'] = ('date_joined', 'last_login', 'last_access',)
        return fieldsets

    def get_username(self, user):
        if hasattr(user, 'customer'):
            return user.customer.get_username()
        return user.get_username()
    get_username.short_description = _("Username")
    get_username.admin_order_field = 'email'

    def salutation(self, user):
        if hasattr(user, 'customer'):
            return user.customer.get_salutation_display()
        return ''
    salutation.short_description = _("Salutation")
    salutation.admin_order_field = 'customer__salutation'

    def recognized(self, user):
        if hasattr(user, 'customer'):
            state = user.customer.get_recognized_display()
            if user.is_staff:
                state = '{}/{}'.format(state, _("Staff"))
            return state
        return _("User")
    recognized.short_description = _("State")

    def last_access(self, user):
        if hasattr(user, 'customer'):
            return localtime(user.customer.last_access).strftime("%d %B %Y %H:%M:%S")
        return _("No data")
    last_access.short_description = _("Last accessed")
    last_access.admin_order_field = 'customer__last_access'

    def is_unexpired(self, user):
        if hasattr(user, 'customer'):
            return not user.customer.is_expired()
        return True
    is_unexpired.short_description = _("Unexpired")
    is_unexpired.boolean = True


class CustomerProxy(get_user_model()):
    """
    With this neat proxy model, we are able to place the Customer Model Admin into
    the section “MyShop” instead of section email_auth.
    """
    class Meta:
        proxy = True
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

try:
    admin.site.unregister(get_user_model())
except admin.sites.NotRegistered:
    pass
