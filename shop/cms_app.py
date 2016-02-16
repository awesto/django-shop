# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class OrderApp(CMSApp):
    name = _("View Orders")
    urls = ['shop.urls.order']
    cache_placeholders = False

apphook_pool.register(OrderApp)
