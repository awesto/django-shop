#!/usr/bin/env python
# vim:fileencoding=utf-8

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class ShopApp(CMSApp):
    name = _("Shop App")
    urls = ["shop.urls"]

apphook_pool.register(ShopApp)