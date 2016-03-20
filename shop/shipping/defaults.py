# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import fields, models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_fsm import transition
from shop.models.order import OrderItemModel
from shop.admin.order import OrderItemInline
from .base import ShippingProvider
from django_fsm.signals import pre_transition


class DefaultShippingProvider(ShippingProvider):
    """
    Default shipping provider for items without explicit shipping.
    """
    namespace = 'default-shipping'


class CancelItemShippingProvider(ShippingProvider):
    """
    Pseudo shipping provider for items which have been canceled for shipping.
    """
    namespace = 'cancel-item-shipping'


class CommissionGoodsWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It adds all the methods required for state transitions, while picking and packing the
    ordered goods for delivery.
    """
    TRANSITION_TARGETS = {
        'pick_goods': _("Picking goods"),
        'pack_goods': _("Packing goods"),
    }

    @transition(field='status', source=['payment_confirmed'], target='pick_goods',
        custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source=['pick_goods'],
        target='pack_goods', custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Change status to 'pack_goods'."""
        print 'transition pick_goods -> pack_goods'

    @receiver(pre_transition)
    def create_model(sender, **kwargs):
        print 'create model'


class OrderItemForm(models.ModelForm):
    """
    """
    cancel = fields.BooleanField(label=_("Cancel this item"), initial=False, required=False)

    class Meta:
        model = OrderItemModel
        exclude = ()

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs.setdefault('initial', {})
            kwargs['initial'].update(delivered=kwargs['instance'].quantity)
        super(OrderItemForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(OrderItemForm, self).clean()
        cleaned_data['delivered'] = min(max(0, cleaned_data['delivered']), self.instance.quantity)
        print 'clean: ', self.instance.order.status
        return cleaned_data


class OrderItemInlineDelivery(OrderItemInline):
    form = OrderItemForm

    def get_fields(self, request, obj=None):
        fields = list(super(OrderItemInlineDelivery, self).get_fields(request, obj))
        if obj and obj.status == 'pick_goods':
            fields[0] += ('cancel',)
            fields[1] += ('delivered',)
        return fields

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(OrderItemInlineDelivery, self).get_readonly_fields(request, obj))
        if obj and obj.status == 'pack_goods':
            fields.append('delivered')
        return fields


class OrderDeliveryAdminMixin(object):
    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for instance in super(OrderDeliveryAdminMixin, self).get_inline_instances(request, obj=None):
            if isinstance(instance, OrderItemInline):
                inline_instances.append(OrderItemInlineDelivery(self.model, self.admin_site))
            else:
                inline_instances.append(instance)
        return inline_instances
