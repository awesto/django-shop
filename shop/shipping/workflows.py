# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Sum
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from django_fsm import transition


class ShippingWorkflowMixinBase(object):
    TRANSITION_TARGETS = {
        'pick_goods': _("Picking goods"),
        'pack_goods': _("Packing goods"),
        'ready_for_delivery': _("Ready for delivery"),
    }


class CommissionGoodsWorkflowMixin(ShippingWorkflowMixinBase):
    """
    Add this class to ``settings.SHOP_ORDER_WORKFLOWS`` to mix it into the merchants Order model.
    It is mutual exclusive with :class:`shop.shipping.workflows.PartialDeliveryWorkflowMixin`.

    It adds all the methods required for state transitions, while picking and packing
    the ordered goods for shipping.
    """
    def ready_for_picking(self):
        return self.is_fully_paid() and self.unfulfilled_items > 0

    @transition(field='status', source=['payment_confirmed'], target='pick_goods',
                custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source=['pick_goods'], target='pack_goods',
                custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Change status to 'pack_goods'."""

    @transition(field='status', source='pack_goods', target='ship_goods',
                custom=dict(admin=True, button_name=_("Ship the goods")))
    def ship_goods(self, by=None):
        """Ship the goods."""

    @transition(field='status', source='ship_goods', target='ready_for_delivery',
                custom=dict(auto=True))
    def prepare_for_delivery(self, by=None):
        """Put the parcel into the outgoing delivery."""


class PartialDeliveryWorkflowMixin(ShippingWorkflowMixinBase):
    """
    Add this class to ``settings.SHOP_ORDER_WORKFLOWS`` to mix it into the merchants Order model.
    It is mutual exclusive with :class:`shop.shipping.workflows.CommissionGoodsWorkflowMixin`.

    This mixin supports partial delivery, hence check that a materialized representation of the
    models :class:`shop.models.delivery.DeliveryModel` and :class:`shop.models.delivery.DeliveryItemModel`
    exists and is instantiated.

    Importing the classes :class:`shop.models.defaults.delivery.DeliveryModel` and
    :class:`shop.models.defaults.delivery_item.DeliveryItemModel` into the merchants
    ``models.py``, usually is enough. This adds all the methods required for state transitions,
    while picking, packing and shipping the ordered goods for delivery.
    """
    @cached_property
    def unfulfilled_items(self):
        unfulfilled_items = 0
        for order_item in self.items.all():
            if not order_item.canceled:
                aggr = order_item.deliveryitem_set.aggregate(delivered=Sum('quantity'))
                unfulfilled_items += order_item.quantity - (aggr['delivered'] or 0)
        return unfulfilled_items

    def ready_for_picking(self):
        return self.is_fully_paid() and self.unfulfilled_items > 0

    def ready_for_shipping(self):
        return self.delivery_set.filter(shipped_at__isnull=True).exists()

    @transition(field='status', source='*', target='pick_goods', conditions=[ready_for_picking],
                custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source=['pick_goods'], target='pack_goods',
                custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Prepare shipping object and change status to 'pack_goods'."""

    @transition(field='status', source='*', target='ship_goods', conditions=[ready_for_shipping],
                custom=dict(admin=True, button_name=_("Ship the goods")))
    def ship_goods(self, by=None):
        """Ship the goods."""

    @transition(field='status', source='ship_goods', target='ready_for_delivery',
                custom=dict(auto=True))
    def prepare_for_delivery(self, by=None):
        """Put the parcel into the outgoing delivery."""
