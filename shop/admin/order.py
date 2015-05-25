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
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('id', 'user__username', 'user__lastname')
    fsm_field = ('status',)
    date_hierarchy = 'created_at'
    inlines = (OrderPaymentInline, OrderItemInline,)
    readonly_fields = ('status', 'user', 'total', 'subtotal', 'created_at', 'updated_at', 'extra',)
    fields = (('created_at', 'updated_at'), 'status', ('subtotal', 'total',), 'user', 'extra',)

    def save_model(self, request, obj, form, change):
        amount_paid = obj.get_amount_paid()
        obj.payment_deposited()
        super(BaseOrderAdmin, self).save_model(request, obj, form, change)
        if obj.get_amount_paid() > amount_paid:
            pass

    def get_form(self, request, obj=None, **kwargs):
        # must add field `extra` on the fly.
        #Form = type('TextLinkForm', (TextLinkFormBase,), {'ProductModel': ProductModel, 'product': product_field})
        #kwargs.update(form=Form)
        return super(BaseOrderAdmin, self).get_form(request, obj, **kwargs)


class OrderAdmin(BaseOrderAdmin):
    search_fields = BaseOrderAdmin.search_fields + ('shipping_address_text', 'billing_address_text')
    fields = BaseOrderAdmin.fields + (('shipping_address_text', 'billing_address_text',),)
