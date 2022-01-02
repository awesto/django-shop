from django.db.models import SET_DEFAULT

# from shop import deferred
# from django.db import models
# from shop.shopmodels.address import BaseShippingAddress, BaseBillingAddress
from shop.shopmodels.cart import BaseCart

from django.db import models
from shop.shopmodels import cart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    # shipping_address = deferred.ForeignKey(
    #     BaseShippingAddress,
    #     on_delete=SET_DEFAULT,
    #     null=True,
    #     default=None,
    #     related_name='+',
    # )
    #
    # billing_address = deferred.ForeignKey(
    #     BaseBillingAddress,
    #     on_delete=SET_DEFAULT,
    #     null=True,
    #     default=None,
    #     related_name='+',
    # )

    shipping_address = models.ForeignKey(
        'ShippingAddress',
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
    )

    billing_address = models.ForeignKey(
        'BillingAddress',
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
    )


class CartItem(cart.BaseCartItem):
    """Default materialized model for CartItem"""
    quantity = models.PositiveIntegerField()
