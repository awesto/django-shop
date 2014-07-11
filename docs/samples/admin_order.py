# -*- coding: utf-8 -*-
from django.contrib import admin
from shop.admin.order import BaseOrderAdmin
from myshop.models.shopmodels import Order


class OrderAdmin(BaseOrderAdmin):
    pass

admin.site.register(Order, OrderAdmin)
