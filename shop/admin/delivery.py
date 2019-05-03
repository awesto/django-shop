# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.forms import models, ValidationError
from django.http import HttpResponse
from django.template.loader import select_template
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from shop.conf import app_settings
from shop.admin.order import OrderItemInline
from shop.models.order import OrderItemModel
from shop.models.delivery import DeliveryModel
from shop.modifiers.pool import cart_modifiers_pool
from shop.serializers.delivery import DeliverySerializer
from shop.serializers.order import OrderDetailSerializer


class OrderItemForm(models.ModelForm):
    """
    This form handles an ordered item, but adds a number field to modify the number of
    items to deliver.
    """
    class Meta:
        model = OrderItemModel
        exclude = ()

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs.setdefault('initial', {})
            deliver_quantity = kwargs['instance'].quantity - self.get_delivered(kwargs['instance'])
            kwargs['initial'].update(deliver_quantity=deliver_quantity)
        else:
            deliver_quantity = None
        super(OrderItemForm, self).__init__(*args, **kwargs)
        if deliver_quantity == 0:
            self['deliver_quantity'].field.widget.attrs.update(readonly='readonly')

    @classmethod
    def get_delivered(cls, instance):
        """
        Returns the quantity already delivered for this order item.
        """
        aggr = instance.deliver_item.aggregate(delivered=Sum('quantity'))
        return aggr['delivered'] or 0

    def clean(self):
        cleaned_data = super(OrderItemForm, self).clean()
        if cleaned_data.get('deliver_quantity') is not None:
            if cleaned_data['deliver_quantity'] < 0:
                raise ValidationError(_("Only a positive number of items can be delivered"), code='invalid')
            if cleaned_data['deliver_quantity'] > self.instance.quantity - self.get_delivered(self.instance):
                raise ValidationError(_("The number of items to deliver exceeds the ordered quantity"), code='invalid')
        return cleaned_data

    def has_changed(self):
        """Force form to changed"""
        return True


class OrderItemInlineDelivery(OrderItemInline):
    def get_fields(self, request, obj=None):
        fields = list(super(OrderItemInlineDelivery, self).get_fields(request, obj))
        if obj:
            if obj.status == 'pick_goods' and obj.unfulfilled_items > 0:
                fields[1] += ('deliver_quantity', 'canceled',)
            else:
                fields[1] += ('get_delivered', 'show_ready',)
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(OrderItemInlineDelivery, self).get_readonly_fields(request, obj))
        if obj:
            if not (obj.status == 'pick_goods' and obj.unfulfilled_items > 0):
                readonly_fields.extend(['get_delivered', 'show_ready'])
        return readonly_fields

    def get_formset(self, request, obj=None, **kwargs):
        """
        Add field `quantity` to the form on the fly, using the same numeric type as `OrderItem.quantity`
        """
        labels = {'quantity': _("Deliver quantity")}
        attrs = models.fields_for_model(obj.items.model, fields=['quantity'], labels=labels)
        # rename to deliver_quantity, since quantity is already used
        attrs['deliver_quantity'] = attrs.pop('quantity')
        if obj.status == 'pick_goods' and obj.unfulfilled_items > 0:
            attrs['deliver_quantity'].widget.attrs.update(style='width: 50px;')
        else:
            attrs['deliver_quantity'].required = False
        form = type(str('OrderItemForm'), (OrderItemForm,), attrs)
        labels = {'canceled': _("Cancel this item")}
        kwargs.update(form=form, labels=labels)
        formset = super(OrderItemInlineDelivery, self).get_formset(request, obj, **kwargs)
        return formset

    def get_delivered(self, obj=None):
        return OrderItemForm.get_delivered(obj)
    get_delivered.short_description = _("Delivered quantity")

    def show_ready(self, obj=None):
        return not obj.canceled
    show_ready.boolean = True
    show_ready.short_description = _("Ready for delivery")


def get_shipping_choices():
    choices = [sm.get_choice() for sm in cart_modifiers_pool.get_shipping_modifiers()]
    return choices


class DeliveryForm(models.ModelForm):
    shipping_method = models.ChoiceField(
        label=_("Shipping by"),
        choices=get_shipping_choices,
    )

    class Meta:
        model = DeliveryModel
        exclude = []

    def has_changed(self):
        return True

    def clean_shipping_method(self):
        if not self.cleaned_data['shipping_method']:
            return self.instance.shipping_method
        return self.cleaned_data['shipping_method']


class DeliveryInline(admin.TabularInline):
    model = DeliveryModel
    form = DeliveryForm
    extra = 0
    fields = ['shipping_id', 'shipping_method', 'delivered_items', 'print_out', 'fulfilled_at', 'shipped_at']
    readonly_fields = ['delivered_items', 'print_out', 'fulfilled_at', 'shipped_at']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        qs = self.model.objects.filter(order=obj)
        return qs.count()

    def get_fields(self, request, obj=None):
        assert obj is not None, "An Order object can not be added through the Django-Admin"
        fields = list(super(DeliveryInline, self).get_fields(request, obj))
        if not obj.allow_partial_delivery:
            fields.remove('delivered_items')
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(DeliveryInline, self).get_readonly_fields(request, obj))
        if not app_settings.SHOP_OVERRIDE_SHIPPING_METHOD or obj.status == 'ready_for_delivery':
            readonly_fields.append('shipping_method')
        return readonly_fields

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(DeliveryInline, self).get_formset(request, obj, **kwargs)
        if not app_settings.SHOP_OVERRIDE_SHIPPING_METHOD or obj.status == 'ready_for_delivery':
            # make readonly field optional
            formset.form.base_fields['shipping_method'].required = False
        return formset

    def delivered_items(self, obj):
        aggr = obj.items.aggregate(quantity=Sum('quantity'))
        aggr['quantity'] = aggr['quantity'] or 0
        aggr.update(items=obj.items.count())
        return '{quantity}/{items}'.format(**aggr)
    delivered_items.short_description = _("Quantity/Items")

    def print_out(self, obj):
        if obj.fulfilled_at is None:
            return ''
        link = reverse('admin:print_delivery_note', args=(obj.id,)), _("Delivery Note")
        return format_html(
            '<span class="object-tools"><a href="{0}" class="viewsitelink" target="_new">{1}</a></span>',
            *link)
    print_out.short_description = _("Print out")

    def fulfilled(self, obj):
        if obj.fulfilled_at:
            return timezone.localtime(obj.fulfilled_at).ctime()  # TODO: find the correct time format
        return _("Pending")
    fulfilled.short_description = _("Fulfilled at")


class DeliveryOrderAdminMixin(object):
    """
    Add this mixin to the class defining the OrderAdmin
    """
    def get_urls(self):
        my_urls = [
            url(r'^(?P<delivery_pk>\d+)/print_delivery_note/$',
                self.admin_site.admin_view(self.render_delivery_note),
                name='print_delivery_note'),
        ]
        my_urls.extend(super(DeliveryOrderAdminMixin, self).get_urls())
        return my_urls

    def render_delivery_note(self, request, delivery_pk=None):
        template = select_template([
            '{}/print/delivery-note.html'.format(app_settings.APP_LABEL.lower()),
            'shop/print/delivery-note.html'
        ])
        delivery = DeliveryModel.objects.get(pk=delivery_pk)
        context = {'request': request, 'render_label': 'print'}
        customer_serializer = app_settings.CUSTOMER_SERIALIZER(delivery.order.customer)
        order_serializer = OrderDetailSerializer(delivery.order, context=context)
        delivery_serializer = DeliverySerializer(delivery, context=context)
        content = template.render({
            'customer': customer_serializer.data,
            'order': order_serializer.data,
            'delivery': delivery_serializer.data,
            'object': delivery,
        })
        return HttpResponse(content)

    def get_inline_instances(self, request, obj=None):
        assert obj is not None, "An Order object can not be added through the Django-Admin"
        assert hasattr(obj, 'associate_with_delivery'), "Add 'shop.shipping.workflows.SimpleShippingWorkflowMixin' " \
            "(or a class inheriting from thereof) to SHOP_ORDER_WORKFLOWS."
        inline_instances = list(super(DeliveryOrderAdminMixin, self).get_inline_instances(request, obj))
        if obj.associate_with_delivery:
            if obj.allow_partial_delivery:
                # replace `OrderItemInline` by `OrderItemInlineDelivery` for that instance.
                inline_instances = [
                    OrderItemInlineDelivery(self.model, self.admin_site) if isinstance(instance, OrderItemInline) else instance
                    for instance in inline_instances
                ]
            inline_instances.append(DeliveryInline(self.model, self.admin_site))
        return inline_instances

    def save_related(self, request, form, formsets, change):
        super(DeliveryOrderAdminMixin, self).save_related(request, form, formsets, change)
        if form.instance.status == 'pack_goods' and 'status' in form.changed_data:
            orderitem_formset = [fs for fs in formsets if issubclass(fs.model, OrderItemModel)][0]
            form.instance.update_or_create_delivery(orderitem_formset.cleaned_data)
