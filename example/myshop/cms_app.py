# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.cms_menus import SoftRootCutter
from menus.menu_pool import menu_pool


class ProductsListApp(CMSApp):
    name = _("Products List")
    urls = ['myshop.urls.{}_products'.format('polymorphic' if settings.SHOP_TUTORIAL == 'polymorphic' else 'simple')]

apphook_pool.register(ProductsListApp)


class ProductSearchApp(CMSApp):
    name = _("Search")
    urls = ['myshop.urls.search']

apphook_pool.register(ProductSearchApp)


def _deregister_menu_pool_modifier(Modifier):
    index = None
    for k, modifier_class in enumerate(menu_pool.modifiers):
        if issubclass(modifier_class, Modifier):
            index = k
    if index is not None:
        # intentionally only modifying the list
        menu_pool.modifiers.pop(index)

_deregister_menu_pool_modifier(SoftRootCutter)
