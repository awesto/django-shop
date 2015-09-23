# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _
from shop.models.customer import CustomerModel


class CustomerInlineAdmin(admin.StackedInline):
    model = CustomerModel
    fields = ('salutation',)


class CustomerChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        exclude = ('email',)

    email = forms.EmailField(required=False)

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
        return CustomerModel.CUSTOMER_STATES

    def queryset(self, request, queryset):
        try:
            custate = int(self.value())
            if custate in dict(CustomerModel.CUSTOMER_STATES):
                queryset = queryset.filter(customer__recognized=custate)
        finally:
            return queryset


class CustomerAdmin(UserAdmin):
    """
    This ModelAdmin class must be registered inside the implementation of this shop.
    """
    form = CustomerChangeForm
    inlines = (CustomerInlineAdmin,)
    list_display = ('identifier', 'salutation', 'last_name', 'first_name', 'recognized',
        'last_access', 'is_unexpired')
    segmentation_list_display = ('identifier',)
    list_filter = UserAdmin.list_filter + (CustomerListFilter,)
    readonly_fields = ('last_login', 'date_joined', 'last_access', 'recognized')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CustomerAdmin, self).get_fieldsets(request, obj=obj)
        fieldsets[0][1]['fields'] = ('username', 'recognized', 'password',)
        fieldsets[3][1]['fields'] = ('date_joined', 'last_login', 'last_access',)
        return fieldsets

    def identifier(self, user):
        return user.customer.identifier()
    identifier.short_description = _("Identifier")

    def salutation(self, user):
        return user.customer.get_salutation_display()
    salutation.short_description = _("Salutation")

    def recognized(self, user):
        state = user.customer.get_recognized_display()
        if user.is_staff:
            state = '{}/{}'.format(state, _("Staff"))
        return state
    recognized.short_description = _("State")

    def last_access(self, user):
        return localtime(user.customer.last_access).strftime("%d %B %Y %H:%M:%S")
    last_access.short_description = _("Last accessed")

    def is_unexpired(self, user):
        return not user.customer.is_expired()
    is_unexpired.short_description = _("Unexpired")
    is_unexpired.boolean = True


class CustomerProxy(get_user_model()):
    """
    With this neat proxy model, we are able to place the Customer Model Admin into
    the section “Shop” instead of section email_auth.
    """
    class Meta:
        proxy = True
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

try:
    admin.site.unregister(get_user_model())
except admin.sites.NotRegistered:
    pass
admin.site.register(CustomerProxy, CustomerAdmin)
