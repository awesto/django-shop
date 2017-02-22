# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.views.dashboard import router, ProductsDashboard

router.register('products', ProductsDashboard, base_name='product')
