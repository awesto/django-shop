# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

# import default models from djangoSHOP to materialize them
from shop.models.defaults.address import Address
from shop.models.defaults.order import Order
from shop.models.defaults.order_shipping import OrderShipping
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.customer import Customer

# models defined by the myshop instance itself
from .order import OrderItem

if settings.SHOP_TUTORIAL == 'simple':
    from .simple.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'i18n':
    from .i18n.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from .polymorphic.smartcard import SmartCard
