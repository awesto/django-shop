# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

CASCADE_PLUGINS = getattr(settings, 'SHOP_CASCADE_PLUGINS',
    ('auth', 'breadcrumb', 'catalog', 'cart', 'checkout', 'order', 'processbar', 'search',))
