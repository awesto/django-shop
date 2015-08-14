# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.forms import widgets
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from fsm_admin.mixins import FSMTransitionMixin
from shop.models.order import OrderItemModel, OrderPayment
from shop.modifiers.pool import cart_modifiers_pool
from shop.rest import serializers


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


class PrintOrderAdminMixin(object):
    """
    A customized OrderAdmin class shall inherit from this mixin class, to add
    methods for printing the delivery note and the invoice.
    """
    def __init__(self, *args, **kwargs):
        self.fields += ('print_out',)
        self.readonly_fields += ('print_out',)
        super(PrintOrderAdminMixin, self).__init__(*args, **kwargs)

    def get_urls(self):
        my_urls = patterns('',
            url(r'^(?P<pk>\d+)/print_delivery_note/$', self.admin_site.admin_view(self.render_delivery_note),
                name='print_delivery_note'),
            url(r'^(?P<pk>\d+)/print_invoice/$', self.admin_site.admin_view(self.render_invoice),
                name='print_invoice'),
        )
        return my_urls + super(PrintOrderAdminMixin, self).get_urls()

    def render_delivery_note(self, request, pk=None):
        order = self.get_object(request, pk)
        order_serializer = serializers.OrderDetailSerializer(order, context={'request': request})
        context = {
            'customer': serializers.CustomerSerializer(order.user).data,
            'data': order_serializer.data,
        }
        return render_to_response('shop/printing/delivery-note.html', context,
            context_instance=RequestContext(request))

    def render_invoice(self, request, pk=None):
        order = self.get_object(request, pk)
        order_serializer = serializers.OrderDetailSerializer(order, context={'request': request})
        context = {
            'customer': serializers.CustomerSerializer(order.user).data,
            'data': order_serializer.data,
        }
        return render_to_response('shop/printing/delivery-note.html', context,
            context_instance=RequestContext(request))

    def print_out(self, obj):
        if obj.status == 'pick_goods':
            button = reverse('admin:print_delivery_note', args=(obj.id,)), _("Delivery Note")
        elif obj.status == 'pack_goods':
            button = reverse('admin:print_invoice', args=(obj.id,)), _("Invoice")
        else:
            button = None
        if button:
            return format_html(
                '<span class="object-tools"><a href="{0}" class="viewsitelink" target="_new">{1}</a></span>',
                *button)
        return ''
    print_out.short_description = _("Print out")
    print_out.allow_tags = True


class OrderAdmin(BaseOrderAdmin):
    """
    Admin class to be used with `shop.models.defauls.order`
    """
    search_fields = BaseOrderAdmin.search_fields + ('shipping_address_text', 'billing_address_text',)
    fields = BaseOrderAdmin.fields + (('shipping_address_text', 'billing_address_text',),)
