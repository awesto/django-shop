# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from shop.admin.customer import CustomerProxy, CustomerAdmin
from . import product

admin.site.register(CustomerProxy, CustomerAdmin)
