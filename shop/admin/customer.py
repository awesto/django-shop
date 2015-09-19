# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from shop.models.customer import CustomerModel


class CustomerInlineAdmin(admin.StackedInline):
    model = CustomerModel


class CustomerChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()


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
    form = CustomerChangeForm
    inlines = (CustomerInlineAdmin,)
    list_display = ('identifier', 'salutation', 'last_name', 'first_name', 'date_joined')
    list_filter = UserAdmin.list_filter + (CustomerListFilter,)

    def identifier(self, user):
        return user.customer.identifier()
    identifier.short_description = _("Identifier")

    def salutation(self, user):
        return user.customer.get_salutation_display()
    salutation.short_description = _("Salutation")
