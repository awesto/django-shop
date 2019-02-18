# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from shop.admin.defaults.order import OrderAdmin
from shop.models.defaults.order import Order
from shop.admin.order import PrintInvoiceAdminMixin


@admin.register(Order)
class OrderAdmin(PrintInvoiceAdminMixin, OrderAdmin):
    pass
