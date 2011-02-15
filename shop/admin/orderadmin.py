#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from shop.models.ordermodel import Order, OrderItem

class OrderAdmin(ModelAdmin):
    pass
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(ModelAdmin):
    pass
admin.site.register(OrderItem, OrderItemAdmin)