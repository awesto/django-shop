# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django_fsm import transition
from .base import ShippingProvider


class DefaultShippingProvider(ShippingProvider):
    """
    Default shipping provider for items without explicit shipping.
    """
    namespace = 'default-shipping'


class CommissionGoodsWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It does not support partial delivery.
    It adds all the methods required for state transitions, while picking and packing
    the ordered goods for shipping.
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
