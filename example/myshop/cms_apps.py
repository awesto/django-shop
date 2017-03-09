# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.cms_menus import SoftRootCutter
from menus.menu_pool import menu_pool


class CatalogListApp(CMSApp):
    name = _("Catalog List")

    def get_urls(self, page=None, language=None, **kwargs):
        if settings.SHOP_TUTORIAL == 'polymorphic':
            return ['myshop.urls.polymorphic_products']
        elif settings.SHOP_TUTORIAL == 'i18n_commodity':
            return ['myshop.urls.i18n_products']
        else:
            return ['myshop.urls.simple_products']

apphook_pool.register(CatalogListApp)


class ProductSearchApp(CMSApp):
    name = _("Search")

    def get_urls(self, page=None, language=None, **kwargs):
        return ['myshop.urls.search']

apphook_pool.register(ProductSearchApp)


class OrderApp(CMSApp):
    name = _("View Orders")
    cache_placeholders = False

    def get_urls(self, page=None, language=None, **kwargs):
        if page and page.reverse_id == 'shop-order-last':
            return ['shop.urls.order_last']
        return ['shop.urls.order']

apphook_pool.register(OrderApp)


def _deregister_menu_pool_modifier(Modifier):
    index = None
    for k, modifier_class in enumerate(menu_pool.modifiers):
        if issubclass(modifier_class, Modifier):
            index = k
    if index is not None:
        # intentionally only modifying the list
        menu_pool.modifiers.pop(index)

_deregister_menu_pool_modifier(SoftRootCutter)
