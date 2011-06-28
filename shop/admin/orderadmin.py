#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.utils.translation import ugettext_lazy as _

from shop.models.ordermodel import (Order, OrderItem,
        OrderExtraInfo, ExtraOrderPriceField, OrderPayment)


class OrderExtraInfoInline(admin.TabularInline):
    model = OrderExtraInfo
    extra = 0


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment 
    extra = 0


class ExtraOrderPriceFieldInline(admin.TabularInline):
    model = ExtraOrderPriceField 
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

#TODO: add ExtraOrderItemPriceField inline, ideas?

class OrderAdmin(ModelAdmin):
    list_display = ('id', 'user', 'status','order_total',
            'payment_method', 'created')
    list_filter = ('status', 'payment_method', )
    search_fields = ('id', 'shipping_address_text', 'user__username')
    date_hierarchy = 'created'
    inlines = (OrderItemInline, OrderExtraInfoInline, 
            ExtraOrderPriceFieldInline, OrderPaymentInline)
    readonly_fields = ('created', 'modified',)
    fieldsets = (
            (None, {'fields': ('user', 'status', 'order_total',
                'order_subtotal', 'payment_method', 'created', 'modified')}),
            (_('Shipping'), {
                'fields': ('shipping_address_text',),
                }),
            (_('Billing'), {
                'fields': ('billing_address_text',)
                }),
            )


admin.site.register(Order, OrderAdmin)
