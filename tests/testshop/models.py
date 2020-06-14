from django.db import models
from shop.models.defaults.commodity import Commodity
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.order import Order
from shop.models.order import BaseOrderItem
from shop.models.defaults.delivery import Delivery
from shop.models.defaults.delivery_item import DeliveryItem
from shop.models.defaults.address import BillingAddress, ShippingAddress
from shop.models.defaults.customer import Customer
from shop.models.inventory import BaseInventory, AvailableProductMixin

__all__ = ['Commodity', 'Cart', 'CartItem', 'Order', 'OrderItem', 'Delivery', 'DeliveryItem',
           'BillingAddress', 'ShippingAddress', 'Customer']


class OrderItem(BaseOrderItem):
    quantity = models.PositiveIntegerField()
    canceled = models.BooleanField(default=False)


class MyProduct(AvailableProductMixin, Commodity):
    pass


class MyProductInventory(BaseInventory):
    product = models.ForeignKey(
        MyProduct,
        on_delete=models.CASCADE,
        related_name='inventory_set',
    )

    quantity = models.PositiveIntegerField(default=0)
