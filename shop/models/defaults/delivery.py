# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from shop.models.delivery import BaseDelivery, BaseDeliveryItem


class Delivery(BaseDelivery):
    """Default materialized model for OrderShipping"""

    def clean(self):
        if self.order._fsm_requested_transition == ('status', 'ship_goods'):
            if self.shipping_id:
                self.shipped_at = timezone.now()
            else:
                msg = _("Please provide a valid Shipping ID")
                raise ValidationError(msg)


class DeliveryItem(BaseDeliveryItem):
    """Default materialized model for ShippedItem"""
    quantity = models.IntegerField(_("Delivered quantity"), default=0)
