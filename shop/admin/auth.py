# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


class CustomerAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('salutation', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('identifier', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_registered', 'groups')
    ordering = ('email',)

    def identifier(self, obj):
        if obj.is_registered:
            return format_html('<strong>{}</strong>', obj.identifier())
        else:
            return format_html('<em>{}</em>', obj.identifier())
    identifier.allow_tags = True
