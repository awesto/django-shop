# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool


class CatalogMenu(CMSAttachMenu):
    name = _("Catalog Menu")

    def get_nodes(self, request):
        try:
            if self.instance.publisher_is_draft:
                productpage_set = self.instance.publisher_public.productpage_set
            else:
                productpage_set = self.instance.productpage_set
        except AttributeError:
            return []
        nodes = []
        for id, productpage in enumerate(productpage_set.all(), 1):
            node = NavigationNode(
                title=productpage.product.product_name,
                url=productpage.product.get_absolute_url(),
                id=id,
            )
            nodes.append(node)
        return nodes

menu_pool.register_menu(CatalogMenu)
