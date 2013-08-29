#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from shop.order_signals import completed, shipped
from shop.admin.mixins import LocalizeDecimalFieldsMixin
from shop.models.ordermodel import (Order, OrderItem,
        OrderExtraInfo, ExtraOrderPriceField, OrderPayment)


class OrderExtraInfoInline(admin.TabularInline):
    model = OrderExtraInfo
    extra = 0


class OrderPaymentInline(LocalizeDecimalFieldsMixin, admin.TabularInline):
    model = OrderPayment
    extra = 0


class ExtraOrderPriceFieldInline(LocalizeDecimalFieldsMixin, admin.TabularInline):
    model = ExtraOrderPriceField
    extra = 0


class OrderItemInline(LocalizeDecimalFieldsMixin, admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)

#TODO: add ExtraOrderItemPriceField inline, ideas?


class OrderAdmin(LocalizeDecimalFieldsMixin, ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_total', 'created')
    list_filter = ('status', 'user')
    search_fields = ('id', 'shipping_address_text', 'user__username')
    date_hierarchy = 'created'
    inlines = (OrderItemInline, OrderExtraInfoInline,
            ExtraOrderPriceFieldInline, OrderPaymentInline)
    readonly_fields = ('created', 'modified',)
    raw_id_fields = ('user',)
    fieldsets = (
            (None, {'fields': ('user', 'status', 'order_total',
                'order_subtotal', 'created', 'modified')}),
            (_('Shipping'), {
                'fields': ('shipping_address_text',),
                }),
            (_('Billing'), {
                'fields': ('billing_address_text',)
                }),
            )

    def save_model(self, request, order, form, change):

        if change:
            pre_save_status = Order.objects.get(pk=order.pk).status
            post_save_status = order.status

        super(OrderAdmin, self).save_model(request, order, form, change)

        if post_save_status == Order.SHIPPED and pre_save_status != Order.SHIPPED:
            shipped.send(sender=self, order=order)

    def save_related(self, request, form, formset, change):
        super(OrderAdmin, self).save_related(request, form, formset, change)

        if form.instance:
            if form.instance.status != Order.SHIPPED:
                if not form.instance.is_completed() and form.instance.is_paid():
                    form.instance.status = Order.COMPLETED
                    form.instance.save()
                    completed.send(sender=self, order=form.instance)

ORDER_MODEL = getattr(settings, 'SHOP_ORDER_MODEL', None)
if not ORDER_MODEL:
    admin.site.register(Order, OrderAdmin)
