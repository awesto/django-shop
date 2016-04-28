# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

# import default models from djangoSHOP to materialize them
from shop.models.defaults.address import ShippingAddress, BillingAddress
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.customer import Customer

# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL == 'commodity' or settings.SHOP_TUTORIAL == 'i18n_commodity':
    from shop.models.defaults.order_item import OrderItem
    from shop.models.defaults.commodity import Commodity
elif settings.SHOP_TUTORIAL == 'smartcard':
    from shop.models.defaults.order_item import OrderItem
    from .smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from shop.models.defaults.order_item import OrderItem
    from .i18n_smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from .polymorphic.order import OrderItem
    from .polymorphic.smartcard import SmartCard
    from .polymorphic.smartphone import SmartPhoneModel, SmartPhone
    from shop.models.defaults.delivery import Delivery, DeliveryItem

from shop.models.defaults.order import Order
