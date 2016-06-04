# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models.fields import Field, FieldDoesNotExist
from django.forms import widgets
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.formats import number_format
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from fsm_admin.mixins import FSMTransitionMixin
from shop.models.customer import CustomerModel
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

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.StackedInline):
    model = OrderItemModel
    extra = 0
    fields = (
        ('product_code', 'unit_price', 'line_total',),
        ('quantity',),
        'get_extra_data',
    )
    readonly_fields = ('product_code', 'quantity', 'unit_price', 'line_total', 'get_extra_data',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        return self.model.objects.filter(order=obj).count()

    def get_extra_data(self, obj):
        return obj.extra  # TODO: use a template to format this data
    get_extra_data.short_description = pgettext_lazy('admin', "Extra data")


class StatusListFilter(admin.SimpleListFilter):
    title = pgettext_lazy('admin', "Status")
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        lookups = dict(model_admin.model._transition_targets)
        lookups.pop('new')
        lookups.pop('created')
        return lookups.items()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class BaseOrderAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ('get_number', 'customer', 'status_name', 'total', 'created_at',)
    list_filter = (StatusListFilter,)
    fsm_field = ('status',)
    date_hierarchy = 'created_at'
    inlines = (OrderItemInline, OrderPaymentInline,)
    readonly_fields = ('get_number', 'status_name', 'get_total', 'get_subtotal', 'get_customer_link',
        'get_outstanding_amount', 'created_at', 'updated_at', 'extra', 'stored_request',)
    fields = ('get_number', 'status_name', ('created_at', 'updated_at'),
        ('get_subtotal', 'get_total', 'get_outstanding_amount',), 'get_customer_link', 'extra', 'stored_request',)
    actions = None

    def get_number(self, obj):
        return obj.get_number()
    get_number.short_description = pgettext_lazy('admin', "Order number")

    def get_total(self, obj):
        return number_format(obj.total)
    get_total.short_description = pgettext_lazy('admin', "Total")

    def get_subtotal(self, obj):
        return number_format(obj.subtotal)
    get_subtotal.short_description = pgettext_lazy('admin', "Subtotal")

    def get_outstanding_amount(self, obj):
        return number_format(obj.outstanding_amount)
    get_outstanding_amount.short_description = pgettext_lazy('admin', "Outstanding amount")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_customer_link(self, obj):
        try:
            url = reverse('admin:shop_customerproxy_change', args=(obj.customer.pk,))
            return format_html('<a href="{0}" target="_new">{1}</a>', url, obj.customer.get_username())
        except NoReverseMatch:
            return format_html('<strong>{0}</strong>', obj.customer.get_username())
    get_customer_link.short_description = pgettext_lazy('admin', "Customer")
    get_customer_link.allow_tags = True

    def get_search_fields(self, request):
        fields = super(BaseOrderAdmin, self).get_search_fields(request) + \
            ('customer__user__email', 'customer__user__last_name',)
        try:
            # if CustomerModel contains a number field, let search for it
            if isinstance(CustomerModel._meta.get_field('number'), Field):
                fields += ('customer__number',)
        except FieldDoesNotExist:
            pass
        return fields


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
        my_urls = [
            url(r'^(?P<pk>\d+)/print_confirmation/$', self.admin_site.admin_view(self.render_confirmation),
                name='print_confirmation'),
            url(r'^(?P<pk>\d+)/print_invoice/$', self.admin_site.admin_view(self.render_invoice),
                name='print_invoice'),
        ] + super(PrintOrderAdminMixin, self).get_urls()
        return my_urls

    def _render_letter(self, request, pk, template):
        order = self.get_object(request, pk)
        context = {'request': request, 'render_label': 'print'}
        order_serializer = serializers.OrderDetailSerializer(order, context=context)
        content = template.render(RequestContext(request, {
            'customer': serializers.CustomerSerializer(order.customer).data,
            'data': order_serializer.data,
            'order': order,
        }))
        return HttpResponse(content)

    def render_confirmation(self, request, pk=None):
        template = select_template([
            '{}/print/order-confirmation.html'.format(settings.SHOP_APP_LABEL.lower()),
            'shop/print/order-confirmation.html'
        ])
        return self._render_letter(request, pk, template)

    def render_invoice(self, request, pk=None):
        template = select_template([
            '{}/print/invoice.html'.format(settings.SHOP_APP_LABEL.lower()),
            'shop/print/invoice.html'
        ])
        return self._render_letter(request, pk, template)

    def print_out(self, obj):
        if obj.status == 'pick_goods':
            button = reverse('admin:print_confirmation', args=(obj.id,)), _("Order Confirmation")
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
    fields = BaseOrderAdmin.fields + (('shipping_address_text', 'billing_address_text',),)

    def get_search_fields(self, request):
        return super(OrderAdmin, self).get_search_fields(request) + \
            ('number', 'shipping_address_text', 'billing_address_text',)
