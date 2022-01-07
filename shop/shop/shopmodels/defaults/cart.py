from django.db.models import SET_DEFAULT
# from collections import OrderedDict

from shop import deferred
# from django.db import models
# from shop.shopmodels.address import BaseShippingAddress, BaseBillingAddress
# from shop.shopmodels.cart import BaseCart

# from shop.shopmodifiers.pool import cart_modifiers_pool
from django.db import models
from shop.shopmodels.cart import BaseCartItem, BaseCart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    shipping_address = deferred.ForeignKey(
        'BaseShippingAddress',
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
        related_name='+',
    )

    billing_address = deferred.ForeignKey(
        'BaseBillingAddress',
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
        related_name='+',
    )

    # shipping_address = models.ForeignKey(
    #     BaseShippingAddress,
    #     on_delete=SET_DEFAULT,
    #     null=True,
    #     default=None,
    # )
    #
    # billing_address = models.ForeignKey(
    #     BaseBillingAddress,
    #     on_delete=SET_DEFAULT,
    #     null=True,
    #     default=None,
    # )


class CartItem(BaseCartItem):
    """Default materialized model for CartItem"""
    # quantity = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=0)
