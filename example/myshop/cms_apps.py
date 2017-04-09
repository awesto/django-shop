# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from cms.apphook_pool import apphook_pool
from cms.cms_menus import SoftRootCutter
from menus.menu_pool import menu_pool

from shop.cms_apphooks import CatalogListCMSApp, CatalogSearchCMSApp, OrderCMSApp


class CatalogListApp(CatalogListCMSApp):
    def get_urls(self, page=None, language=None, **kwargs):
        if settings.SHOP_TUTORIAL in ['i18n_polymorphic', 'polymorphic']:
            return ['myshop.urls.polymorphic_products']
        elif settings.SHOP_TUTORIAL == 'i18n_commodity':
            return ['myshop.urls.i18n_products']
        else:
            return ['myshop.urls.simple_products']

apphook_pool.register(CatalogListApp)


class CatalogSearchApp(CatalogSearchCMSApp):
    def get_urls(self, page=None, language=None, **kwargs):
        return ['myshop.urls.search']
        # TODO: can be simplified into, after merging https://github.com/divio/django-cms/pull/5898
        # from django.conf.urls import url
        # from shop.search.views import SearchView
        # from myshop.serializers import ProductSearchSerializer
        # return [
        #     url(r'^', SearchView.as_view(
        #         serializer_class=ProductSearchSerializer,
        #     )),
        # ]

apphook_pool.register(CatalogSearchApp)


class OrderApp(OrderCMSApp):
    pass

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
