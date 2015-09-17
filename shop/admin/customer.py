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


class CustomerAdmin(UserAdmin):
    form = CustomerChangeForm
    inlines = (CustomerInlineAdmin,)
    #fieldsets = (
    #    (None, {'fields': ('user__email', 'user__password')}),
    #    (_('Personal info'), {'fields': ('salutation', 'user__first_name', 'user__last_name',)}),
    #    #(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    #    #(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    #)
