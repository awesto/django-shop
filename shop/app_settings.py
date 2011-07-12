# -*- coding: utf-8 -*-
"""
Settings for the django-shop application. For documentation please see 
``/docs/settings.rst``.
"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


BASE_ADDRESS_TEMPLATE = \
_("""
Name: %(name)s,
Address: %(address)s,
Zip-Code: %(zipcode)s,
City: %(city)s,
State: %(state)s,
Country: %(country)s
""")

ADDRESS_TEMPLATE = getattr(settings, 'SHOP_ADDRESS_TEMPLATE',
                           BASE_ADDRESS_TEMPLATE)

ORDER_MODEL = getattr(settings, 'SHOP_ORDER_MODEL', None)

CART_MODIFIERS = getattr(settings, 'SHOP_CART_MODIFIERS', None)
