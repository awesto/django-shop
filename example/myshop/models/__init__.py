# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

# import default models from shop to materialize them
from shop.models.defaults.address import ShippingAddress, BillingAddress
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.customer import Customer

__all__ = ['ShippingAddress', 'BillingAddress', 'Cart', 'CartItem', 'Customer', 'OrderItem',
           'Commodity', 'SmartCard', 'SmartPhoneModel', 'SmartPhoneVariant', 'Delivery', 'DeliveryItem']

# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL == 'commodity' or settings.SHOP_TUTORIAL == 'i18n_commodity':
    from shop.models.defaults.order_item import OrderItem
    from shop.models.defaults.commodity import Commodity

elif settings.SHOP_TUTORIAL == 'smartcard':
    from shop.models.defaults.order_item import OrderItem
    from .smartcard import SmartCard

elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from shop.models.defaults.order_item import OrderItem
    if settings.USE_I18N:
        from .i18n_smartcard import SmartCard
    else:
        from .smartcard import SmartCard

if settings.SHOP_TUTORIAL == 'polymorphic':
    if settings.USE_I18N:
        from .i18n_polymorphic.order import OrderItem
        from .i18n_polymorphic.product import Product
        from .i18n_polymorphic.commodity import Commodity
        from .i18n_polymorphic.smartcard import SmartCard
        from .i18n_polymorphic.smartphone import SmartPhoneModel, SmartPhoneVariant
    else:
        from .polymorphic_.order import OrderItem
        from .polymorphic_.product import Product
        from .polymorphic_.commodity import Commodity
        from .polymorphic_.smartcard import SmartCard
        from .polymorphic_.smartphone import SmartPhoneModel, SmartPhoneVariant
    __all__.extend(['SmartCard', 'SmartPhoneModel', 'SmartPhoneVariant'])

if settings.SHOP_PARTIAL_DELIVERY:
    from shop.models.defaults.delivery import Delivery
    from shop.models.defaults.delivery_item import DeliveryItem
    __all__.extend(['Delivery', 'DeliveryItem'])
elif 'shop_sendcloud' in settings.INSTALLED_APPS:
    from shop.models.defaults.delivery import Delivery
    __all__.append('Delivery')
