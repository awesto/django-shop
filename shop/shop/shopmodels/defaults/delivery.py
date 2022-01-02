# from django.utils.translation import gettext_lazy as _
from shop.shopmodels.delivery import BaseDelivery

from django.db import models
# from django.utils.translation import gettext_lazy as _
from shop.shopmodels.delivery import BaseDeliveryItem


class Delivery(BaseDelivery):
    """Default materialized model for OrderShipping"""
    class Meta(BaseDelivery.Meta):
        # verbose_name = _("Delivery")
        # verbose_name_plural = _("Deliveries")
        pass


class DeliveryItem(BaseDeliveryItem):
    """Default materialized model for ShippedItem"""
    # quantity = models.IntegerField(
    #     _("Delivered quantity"),
    #     default=0,
    # )

    quantity = models.PositiveIntegerField(default=0)
