# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models.delivery import BaseDelivery, BaseDeliveryItem


class Delivery(BaseDelivery):
    """Default materialized model for OrderShipping"""


class DeliveryItem(BaseDeliveryItem):
    """Default materialized model for ShippedItem"""
    quantity = models.IntegerField(_("Delivered quantity"), default=0)
