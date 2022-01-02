from django.db import models
from shop.shopmodels.defaults.commodity import Commodity
# from shop.shopmodels.defaults.cart import Cart
from shop.shopmodels.defaults.cart import Cart, CartItem
# from shop.shopmodels.defaults.order import Order
from shop.shopmodels.defaults.order import Order, OrderItem
# from shop.shopmodels.defaults.order_item import OrderItem
# from shop.shopmodels.defaults.delivery import Delivery
from shop.shopmodels.defaults.delivery import Delivery, DeliveryItem
from shop.shopmodels.defaults.product import Product
from shop.shopmodels.defaults.address import BillingAddress, ShippingAddress
from shop.shopmodels.defaults.customer import Customer
from shop.shopmodels.inventory import BaseInventory, AvailableProductMixin

__all__ = ['Commodity', 'Cart', 'CartItem', 'Order', 'OrderItem', 'Delivery', 'DeliveryItem',
           'BillingAddress', 'ShippingAddress', 'Customer', 'Product']


# class OrderItem(BaseOrderItem):
#     quantity = models.PositiveIntegerField()
#     canceled = models.BooleanField(default=False)


class MyProduct(AvailableProductMixin, Commodity):
    pass


class MyProductInventory(BaseInventory):
    product = models.ForeignKey(
        MyProduct,
        on_delete=models.CASCADE,
        related_name='inventory_set',
    )

    quantity = models.PositiveIntegerField(default=0)
