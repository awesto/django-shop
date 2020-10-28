from django.db.models import PositiveIntegerField
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from shop.models import order


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""
    quantity = PositiveIntegerField(_("Ordered quantity"))

    class Meta:
        verbose_name = pgettext_lazy('order_models', "Ordered Item")
        verbose_name_plural = pgettext_lazy('order_models', "Ordered Items")
