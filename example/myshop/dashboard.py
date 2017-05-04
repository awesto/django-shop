# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.views import dashboard

from myshop.serializers.polymorphic import SmartCardSerializer, SmartPhoneSerializer


class ProductsDashboard(dashboard.ProductsDashboard):
    list_display = ['media', 'product_name', 'caption', 'price']
    list_display_links = ['product_name']
    detail_serializer_classes = {
        'myshop.smartcard': SmartCardSerializer,
        'myshop.smartphonemodel': SmartPhoneSerializer,
    }

router = dashboard.DashboardRouter()
router.register('products', ProductsDashboard)
