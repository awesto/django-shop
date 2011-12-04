# -*- coding: utf-8 -*-
"""
This overrides the various models with classes loaded from the corresponding
setting if it exists.
"""
from django.conf import settings
from shop.util.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
# Cart model
CART_MODEL = getattr(settings, 'SHOP_CART_MODEL',
    'shop.models.defaults.cart.Cart')
Cart = load_class(CART_MODEL, 'SHOP_CART_MODEL')

# Cart item model
CARTITEM_MODEL = getattr(settings, 'SHOP_CARTITEM_MODEL',
    'shop.models.defaults.cartitem.CartItem')
CartItem = load_class(CARTITEM_MODEL, 'SHOP_CARTITEM_MODEL')
