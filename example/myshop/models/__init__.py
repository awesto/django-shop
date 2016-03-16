# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

# import default models from djangoSHOP to materialize them
from shop.models.defaults.address import ShippingAddress, BillingAddress
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.order import Order
from shop.models.defaults.customer import Customer

# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL == 'simple':
    from .simple.order import OrderItem
    from .simple.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'i18n':
    from .simple.order import OrderItem
    from .i18n.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from .polymorphic.order import OrderItem
    from .polymorphic.smartcard import SmartCard
    from .polymorphic.smartphone import SmartPhoneModel, SmartPhone
