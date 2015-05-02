# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from shop.order_signals import completed
from shop.models.order import BaseOrder, BaseOrderItem, OrderPayment


# class OrderAnnotationInline(admin.TabularInline):
#     model = OrderAnnotation
#     extra = 0


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0


# class OrderExtraRowInline(admin.TabularInline):
#     model = getattr(BaseOrderExtraRow, '_materialized_model')
#     extra = 0


class OrderItemInline(admin.TabularInline):
    model = getattr(BaseOrderItem, '_materialized_model')
    extra = 0
    raw_id_fields = ('product',)

# TODO: add ExtraOrderItemPriceField inline, ideas?


class BaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('id', 'shipping_address_text', 'user__username')
    date_hierarchy = 'created_at'
    inlines = (OrderItemInline, OrderPaymentInline)
    readonly_fields = ('created_at', 'updated_at',)
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'status', 'total', 'subtotal', 'created_at',
                           'updated_at',)}),
        (_("Shipping"), {'fields': ('shipping_address_text',)}),
        (_("Invoice"), {'fields': ('invoice_address_text',)}),
    )

    def save_model(self, request, order, form, change):
        super(BaseOrderAdmin, self).save_model(request, order, form, change)
        if not order.is_completed() and order.is_paid():
            order.status = BaseOrder.COMPLETED
            order.save()
            completed.send(sender=self, order=order)
