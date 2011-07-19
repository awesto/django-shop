# -*- coding: utf-8 -*-
from django.conf import settings
from shop.util.loader import load_class



#===============================================================================
# Extensibility
#===============================================================================
"""
This overrides the Product model with the class loaded from the SHOP_PRODUCT_MODEL
setting if it exists.
"""
PRODUCT_MODEL = getattr(settings, 'SHOP_PRODUCT_MODEL', 'shop.models.defaults.product.Product')
Product = load_class(PRODUCT_MODEL, 'SHOP_PRODUCT_MODEL')
