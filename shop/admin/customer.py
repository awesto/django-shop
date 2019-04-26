# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django.utils.encoding import force_str
from django.utils.timezone import localtime
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

from shop.models.customer import CustomerModel, CustomerState


class CustomerInlineAdminBase(admin.StackedInline):
    model = CustomerModel
    fieldsets = [
        (None, {'fields': ['get_number']}),
    ]
    readonly_fields = ['get_number']

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj is None else 1

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_number(self, customer):
        return customer.get_number()
    get_number.short_description = pgettext_lazy('customer', "Number")


class CustomerCreationForm(UserCreationForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()


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
        return self.cleaned_data.get('email').strip()


class CustomerListFilter(admin.SimpleListFilter):
    title = _("Customer State")
    parameter_name = 'custate'

    def lookups(self, request, model_admin):
        return CustomerState.choices

    def queryset(self, request, queryset):
        try:
            queryset = queryset.filter(customer__recognized=CustomerState(int(self.value())))
        finally:
            return queryset


class CustomerAdminBase(UserAdmin):
    """
    This ModelAdmin class must be extended and registered inside the merchant's implementation.
    Since the customer model can differ, the field `inlines` must be specified, for instance
    ```
    @admin.register(CustomerProxy)
    class CustomerAdmin(CustomerAdminBase):
        inlines = [CustomerInlineAdminBase]
    ```
    """
    form = CustomerChangeForm
    add_form = CustomerCreationForm
    list_display = ['get_username', 'last_name', 'first_name', 'recognized', 'last_access', 'is_unexpired']
    segmentation_list_display = ['get_username']
    list_filter = list(UserAdmin.list_filter) + [CustomerListFilter]
    readonly_fields = ['last_login', 'date_joined', 'last_access', 'recognized']
    ordering = ['id']

    class Media:
        js = ['shop/js/admin/customer.js']

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super(CustomerAdminBase, self).get_fieldsets(request, obj=obj))
        if obj:
            fieldsets[0][1]['fields'] = ['username', 'recognized', 'password']
            fieldsets[3][1]['fields'] = ['date_joined', 'last_login', 'last_access']
            if not obj.has_usable_password():
                fieldsets.pop(2)
        return fieldsets

    def get_username(self, user):
        return str(user)
    get_username.short_description = _("Username")
    get_username.admin_order_field = 'email'

    def recognized(self, user):
        if user.is_superuser:
            user_state = _("Administrator")
        elif user.is_staff:
            user_state = _("Staff")
        else:
            user_state = _("User")
        if hasattr(user, 'customer'):
            customer_state = force_str(user.customer.recognized)
            if user.is_staff or user.is_superuser:
                return '{}/{}'.format(customer_state, user_state)
            return customer_state
        return user_state
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

    def save_related(self, request, form, formsets, change):
        if hasattr(form.instance, 'customer') and (form.instance.is_staff or form.instance.is_superuser):
            form.instance.customer.recognized = CustomerState.REGISTERED
        super(CustomerAdminBase, self).save_related(request, form, formsets, change)


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
