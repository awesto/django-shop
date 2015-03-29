# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


class CustomerAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('salutation', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'salutation', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)

    def get_queryset(self, request):
        """
        Restrict queryset to real users.
        """
        qs = super(CustomerAdmin, self).get_queryset(request)
        return qs.filter(username__isnull=False)
