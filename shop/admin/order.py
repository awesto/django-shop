# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.forms import widgets
from fsm_admin.mixins import FSMTransitionMixin
from shop.models.order import OrderItemModel, OrderPayment
from shop.modifiers.pool import cart_modifiers_pool


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0
    fields = ('amount', 'transaction_id', 'payment_method', 'created_at',)
    readonly_fields = ('created_at',)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Convert the field `payment_method` into a select box with all possible payment methods.
        """
        choices = [pm.get_choice() for pm in cart_modifiers_pool.get_payment_modifiers()]
        kwargs.update(widgets={'payment_method': widgets.Select(choices=choices)})
        formset = super(OrderPaymentInline, self).get_formset(request, obj, **kwargs)
        return formset


class OrderItemInline(admin.StackedInline):
    model = OrderItemModel
    extra = 0
    readonly_fields = ('product_identifier', 'product_name', 'unit_price', 'line_total', 'extra',)
    fields = (
        ('product_identifier', 'product_name',),
        ('quantity', 'unit_price', 'line_total',),
        'extra',
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(OrderItemInline, self).get_formset(request, obj, **kwargs)
        return formset


class BaseOrderAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'status_name', 'total', 'created_at',)
    list_filter = ('status', 'user',)
    search_fields = ('id', 'user__username', 'user__lastname',)
    fsm_field = ('status',)
    date_hierarchy = 'created_at'
    inlines = (OrderItemInline, OrderPaymentInline,)
    readonly_fields = ('status_name', 'user', 'total', 'subtotal', 'created_at', 'updated_at',
        'extra', 'stored_request',)
    fields = ('status_name', ('created_at', 'updated_at'), ('subtotal', 'total',), 'user',
        'extra', 'stored_request',)

    def get_form(self, request, obj=None, **kwargs):
        # must add field `extra` on the fly.
        #Form = type('TextLinkForm', (TextLinkFormBase,), {'ProductModel': ProductModel, 'product': product_field})
        #kwargs.update(form=Form)
        return super(BaseOrderAdmin, self).get_form(request, obj, **kwargs)


class OrderAdmin(BaseOrderAdmin):
    """
    Admin class to be used with `shop.models.defauls.order`
    """
    search_fields = BaseOrderAdmin.search_fields + ('shipping_address_text', 'billing_address_text',)
    fields = BaseOrderAdmin.fields + (('shipping_address_text', 'billing_address_text',),)
