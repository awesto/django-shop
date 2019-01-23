# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from shop.admin.defaults.order import OrderAdmin
from shop.models.defaults.order import Order
from shop.admin.order import PrintOrderAdminMixin


@admin.register(Order)
class OrderAdmin(PrintOrderAdminMixin, OrderAdmin):
    pass
