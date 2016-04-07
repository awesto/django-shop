# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from shop.admin.customer import CustomerProxy, CustomerAdmin
from shop.models.order import OrderModel
from . import properties

if settings.SHOP_TUTORIAL == 'simple':
    from .simple import smartcard, order
elif settings.SHOP_TUTORIAL == 'i18n':
    from .i18n import smartcard
    from .simple import order
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from .polymorphic import product, order

admin.site.register(CustomerProxy, CustomerAdmin)
