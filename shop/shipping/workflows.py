# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Sum
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from django_fsm import transition

from shop.models.delivery import DeliveryModel


class CommissionGoodsWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It does not support partial delivery.
    It adds all the methods required for state transitions, while picking and packing
    the ordered goods for shipping.
    """
    TRANSITION_TARGETS = {
        'pick_goods': _("Picking goods"),
        'ready_for_delivery': _("Ready for delivery"),
    }

    @transition(field='status', source=['payment_confirmed'], target='pick_goods',
                custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source=['pick_goods'], target='ready_for_delivery',
                custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Change status to 'pack_goods'."""


class PartialDeliveryWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into the `OrderModel`.
    This mixin supports partial delivery, hence the model `Delivery` and `DeliveryItem` must
    be materialized.
    It adds all the methods required for state transitions, while picking, packing and shipping
    the ordered goods for delivery.
    """
    TRANSITION_TARGETS = {
        'pick_goods': _("Picking goods"),
        'ready_for_delivery': _("Ready for delivery"),
    }

    @cached_property
    def unfulfilled_items(self):
        unfulfilled_items = 0
        for order_item in self.items.all():
            if not order_item.canceled:
                aggr = order_item.deliveryitem_set.aggregate(delivered=Sum('quantity'))
                unfulfilled_items += order_item.quantity - (aggr['delivered'] or 0)
        return unfulfilled_items

    def ready_for_delivery(self):
        return self.is_fully_paid() and self.unfulfilled_items > 0

    @transition(field='status', source=['payment_confirmed', 'ready_for_delivery', 'ship_goods'],
                target='pick_goods', conditions=[ready_for_delivery],
                custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""
        shipping_method = self.extra.get('shipping_modifier')
        if shipping_method:
            DeliveryModel.objects.get_or_create(order=self, defaults={'shipping_method': shipping_method})

    @transition(field='status', source=['pick_goods'], target='ready_for_delivery',
                custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Prepare shipping object and change status to 'pack_goods'."""
        self._transition_to_pack_goods = True  # hack to determine this transition in admin backend
