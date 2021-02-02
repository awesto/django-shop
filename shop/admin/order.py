from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import Field
from django.forms import widgets
from django.http import HttpResponse
from django.template.loader import select_template
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from django.utils.translation import pgettext_lazy

from fsm_admin.mixins import FSMTransitionMixin

from shop.conf import app_settings
from shop.models.customer import CustomerModel
from shop.models.order import OrderItemModel, OrderPayment
from shop.modifiers.pool import cart_modifiers_pool
from shop.serializers.order import OrderDetailSerializer
from shop.transition import transition_change_notification


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        """
        Convert the field `payment_method` into a select box with all possible payment methods.
        """
        choices = [pm.get_choice() for pm in cart_modifiers_pool.get_payment_modifiers()]
        kwargs.update(widgets={'payment_method': widgets.Select(choices=choices)})
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def has_add_permission(self, request, obj=None):
        assert obj is not None, "An Order object can not be added through the Django-Admin"
        return obj.status in ['awaiting_payment', 'refund_payment']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        qs = self.model.objects.filter(order=obj)
        if self.has_add_permission(request, obj):
            return qs.count() + 1
        return qs.count()

    def get_fields(self, request, obj=None):
        if self.has_add_permission(request, obj):
            return ['amount', 'transaction_id', 'payment_method', 'created_at']
        return ['get_amount', 'transaction_id', 'payment_method', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        if self.has_add_permission(request, obj):
            return ['created_at', 'get_amount']
        # unless we expect a payment, set all fields as readonly
        return self.get_fields(request, obj)

    def get_amount(self, obj):
        """Return amount using correct local format"""
        return obj.amount
    get_amount.short_description = pgettext_lazy('admin', "Amount Paid")


class OrderItemInline(admin.StackedInline):
    model = OrderItemModel
    extra = 0
    fields = [
        ('product_code', 'unit_price', 'line_total',),
        ('quantity',),
        'render_as_html_extra',
    ]
    readonly_fields = ['product_code', 'quantity', 'unit_price', 'line_total', 'render_as_html_extra']
    template = 'shop/admin/edit_inline/stacked-order.html'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        return self.model.objects.filter(order=obj).count()

    def render_as_html_extra(self, obj):
        item_extra_template = select_template([
            '{0}/admin/orderitem-{1}-extra.html'.format(app_settings.APP_LABEL, obj.product.product_model),
            '{0}/admin/orderitem-product-extra.html'.format(app_settings.APP_LABEL),
            'shop/admin/orderitem-product-extra.html',
        ])
        return item_extra_template.render(obj.extra)
    render_as_html_extra.short_description = pgettext_lazy('admin', "Extra data")


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
    list_display = ['get_number', 'customer', 'status_name', 'get_total', 'created_at']
    list_filter = [StatusListFilter]
    fsm_field = ['status']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ['get_number', 'status_name', 'get_total', 'get_subtotal',
                       'get_customer_link', 'get_outstanding_amount', 'created_at', 'updated_at',
                       'render_as_html_extra', 'stored_request', 'is_fully_paid']
    fields = ['get_number', 'status_name',
              ('created_at', 'updated_at'),
              'get_customer_link',
              ('get_subtotal', 'get_total', 'get_outstanding_amount', 'is_fully_paid'),
              'render_as_html_extra', 'stored_request']
    actions = None
    change_form_template = 'shop/admin/change_form.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_template = select_template([
            '{}/admin/order-extra.html'.format(app_settings.APP_LABEL),
            'shop/admin/order-extra.html',
        ])

    def get_number(self, obj):
        return obj.get_number()
    get_number.short_description = pgettext_lazy('admin', "Order number")

    def get_total(self, obj):
        return str(obj.total)
    get_total.short_description = pgettext_lazy('admin', "Total")

    def get_subtotal(self, obj):
        return str(obj.subtotal)
    get_subtotal.short_description = pgettext_lazy('admin', "Subtotal")

    def get_outstanding_amount(self, obj):
        return str(obj.outstanding_amount)
    get_outstanding_amount.short_description = pgettext_lazy('admin', "Outstanding amount")

    def is_fully_paid(self, obj):
        return obj.is_fully_paid()
    is_fully_paid.short_description = pgettext_lazy('admin', "Is fully paid")
    is_fully_paid.boolean = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def render_as_html_extra(self, obj):
        return self.extra_template.render(obj.extra)
    render_as_html_extra.short_description = pgettext_lazy('admin', "Extra data")

    def get_customer_link(self, obj):
        try:
            url = reverse('admin:shop_customerproxy_change', args=(obj.customer.pk,))
            return format_html('<a href="{0}" target="_new">{1}</a>', url, obj.customer.get_username())
        except NoReverseMatch:
            return format_html('<strong>{0}</strong>', obj.customer.get_username())
    get_customer_link.short_description = pgettext_lazy('admin', "Customer")

    def get_search_fields(self, request):
        search_fields = list(super().get_search_fields(request))
        search_fields.extend(['customer__user__email', 'customer__user__last_name'])
        try:
            # if CustomerModel contains a number field, let search for it
            if isinstance(CustomerModel._meta.get_field('number'), Field):
                search_fields.append('customer__number')
        except FieldDoesNotExist:
            pass
        return search_fields

    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super().get_form(request, obj, **kwargs)
        if obj:
            # store the requested transition inside the instance, so that the model's `clean()` method can access it
            obj._fsm_requested_transition = self._get_requested_transition(request)
        return ModelForm

    def change_view(self, request, object_id, form_url='', extra_context=None):
        assert object_id, "An Order object can not be added through the Django-Admin"
        current_status = self.get_object(request, object_id).status
        response = super().change_view(request, object_id, form_url, extra_context)
        order = self.get_object(request, object_id)
        if current_status != order.status:
            transition_change_notification(order)
        return response


class PrintInvoiceAdminMixin:
    """
    A customized OrderAdmin class shall inherit from this mixin class, to add
    methods for printing the the invoice.
    """
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        fields.append('print_out')
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.append('print_out')
        return readonly_fields

    def get_urls(self):
        my_urls = [
            url(r'^(?P<pk>\d+)/print_invoice/$', self.admin_site.admin_view(self.render_invoice),
                name='print_invoice'),
        ]
        my_urls.extend(super().get_urls())
        return my_urls

    def _render_content(self, request, pk, template):
        order = self.get_object(request, pk)
        context = {'request': request, 'render_label': 'print'}
        customer_serializer = app_settings.CUSTOMER_SERIALIZER(order.customer)
        order_serializer = OrderDetailSerializer(order, context=context)
        return template.render(context={
            'customer': customer_serializer.data,
            'order': order_serializer.data,
            'object': order,
        }, request=request)

    def render_invoice(self, request, pk=None):
        template = select_template([
            '{}/print/invoice.html'.format(app_settings.APP_LABEL.lower()),
            'shop/print/invoice.html'
        ])
        content = self._render_content(request, pk, template)
        return HttpResponse(content)

    def print_out(self, obj):
        if obj.status in ['ready_for_delivery']:
            link = reverse('admin:print_invoice', args=(obj.id,)), pgettext_lazy('admin', "Invoice")
            return format_html(
                '<span class="object-tools"><a href="{0}" class="viewsitelink" target="_new">{1}</a></span>',
                *link)
        return ''
    print_out.short_description = pgettext_lazy('admin', "Print out")
