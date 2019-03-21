# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from shop.models.delivery import BaseDelivery


class Delivery(BaseDelivery):
    """Default materialized model for OrderShipping"""
    class Meta(BaseDelivery.Meta):
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")
