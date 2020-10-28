from django.db.models import SET_DEFAULT

from shop import deferred
from shop.models.address import BaseShippingAddress, BaseBillingAddress
from shop.models.cart import BaseCart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    shipping_address = deferred.ForeignKey(
        BaseShippingAddress,
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
        related_name='+',
    )

    billing_address = deferred.ForeignKey(
        BaseBillingAddress,
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
        related_name='+',
    )
