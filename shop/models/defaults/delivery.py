# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shop.models.delivery import BaseDelivery


class Delivery(BaseDelivery):
    """Default materialized model for OrderShipping"""

    def clean(self):
        if self.order._fsm_requested_transition == ('status', 'ship_goods'):
            if self.shipping_id:
                if not self.shipped_at:
                    self.shipped_at = timezone.now()
            else:
                msg = _("Please provide a valid Shipping ID")
                raise ValidationError(msg)
