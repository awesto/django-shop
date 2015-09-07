# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from shop.models.customer import CustomerModel as Customer

class CustomerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Customer, CustomerAdmin)

