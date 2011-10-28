# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _
from shop.models.productmodel import Product
from shop.util.fields import CurrencyField
from shop.util.loader import load_class
import django


        
#===============================================================================
# Extensibility
#===============================================================================
"""
This overrides the various models with classes loaded from the corresponding
setting if it exists.
"""
# Order model
ORDER_MODEL = getattr(settings, 'SHOP_ORDER_MODEL', 'shop.models.defaults.order.Order')
Order = load_class(ORDER_MODEL, 'SHOP_ORDER_MODEL')
    
# Order item model
ORDERITEM_MODEL = getattr(settings, 'SHOP_ORDERITEM_MODEL', 'shop.models.defaults.orderitem.OrderItem')
OrderItem = load_class(ORDERITEM_MODEL, 'SHOP_ORDERITEM_MODEL')

# Order item model
ORDEREXTRAINFO_MODEL = getattr(settings, 'SHOP_ORDEREXTRAINFO_MODEL', 
                               'shop.models.defaults.orderextras.OrderExtraInfo')
OrderExtraInfo = load_class(ORDEREXTRAINFO_MODEL, 'SHOP_ORDEREXTRAINFO_MODEL')

# Order item model
EXTRAORDERPRICEFIELD_MODEL = getattr(settings, 'SHOP_EXTRAORDERPRICEFIELD_MODEL', 
                                     'shop.models.defaults.orderextras.ExtraOrderPriceField')
ExtraOrderPriceField = load_class(EXTRAORDERPRICEFIELD_MODEL, 'SHOP_EXTRAORDERPRICEFIELD_MODEL')

# Order item model
EXTRAORDERITEMPRICEFIELD_MODEL = getattr(settings, 'SHOP_EXTRAORDERITEMPRICEFIELD_MODEL', 
                                         'shop.models.defaults.orderextras.ExtraOrderItemPriceField')
ExtraOrderItemPriceField = load_class(EXTRAORDERITEMPRICEFIELD_MODEL , 
                                      'SHOP_EXTRAORDERITEMPRICEFIELD_MODEL')

# Order item model
ORDERPAYMENT_MODEL = getattr(settings, 'SHOP_ORDERPAYMENT_MODEL', 
                             'shop.models.defaults.orderextras.OrderPayment')
OrderPayment = load_class(ORDERPAYMENT_MODEL, 'SHOP_ORDERPAYMENT_MODEL')


# Now we clear refrence to product from every OrderItem
def clear_products(sender, instance, using, **kwargs):
    for oi in OrderItem.objects.filter(product=instance):
        oi.product = None
        oi.save()

if LooseVersion(django.get_version()) < LooseVersion('1.3'):
    pre_delete.connect(clear_products, sender=Product)

