from django.db import models
from django.utils.translation import gettext_lazy as _
from shop.models.delivery import BaseDeliveryItem


class DeliveryItem(BaseDeliveryItem):
    """Default materialized model for ShippedItem"""
    quantity = models.IntegerField(
        _("Delivered quantity"),
        default=0,
    )
