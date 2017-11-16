# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool


class DocumentationMenu(CMSAttachMenu):
    name = _("Documentation Menu")  # give the menu a name this is required.

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        nodes = []
        docsmap_file = os.path.join(settings.DOCS_ROOT, 'docsmap.json')
        if not os.path.exists(docsmap_file):
            return
        with io.open(docsmap_file) as fh:
            docs_map = json.load(fh, encoding='utf-8')

        for counter, items in enumerate(docs_map.items(), 1):
            bits = items[0].split('/')
            if len(bits) == 1 and bits[0] == 'index' or len(bits) == 2 and bits[1] != 'index':
                continue
            node = NavigationNode(
                title=items[1],
                url=reverse('documentation', args=(bits[0],)),
                id=counter,
            )
            nodes.append(node)
        return nodes

menu_pool.register_menu(DocumentationMenu)
