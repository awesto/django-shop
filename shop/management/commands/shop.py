# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    help = _("Collect information about all customers which accessed this shop.")

    def add_arguments(self, parser):
        parser.add_argument("subcommand", help=_("./manage.py shop [customers|]"))

    def handle(self, verbosity, subcommand, *args, **options):
        if subcommand == 'check-pages':
            self.check_pages()
        else:
            msg = "Unknown sub-command for shop. Use one of: check-pages create-pages"
            self.stderr.write(msg.format(subcommand))

    def check_pages(self):
        from cms.models.pagemodel import Page
        from shop.cms_apphooks import CatalogListCMSApp, CatalogSearchCMSApp, OrderApp, PasswordResetApp
        from cms.apphook_pool import apphook_pool

        required_apps = [CatalogListCMSApp, CatalogSearchCMSApp, OrderApp, PasswordResetApp]
        apphooks = [(apphook_pool.get_apphook(ah), name) for ah, name in apphook_pool.get_apphooks()]
        for apphook, name in apphooks:
            if isinstance(apphook, CatalogListCMSApp):
                required_apps.remove(CatalogListCMSApp)
                catalog_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if not catalog_pages.exists():
                    msg = "At least one CMS page should have an Application of type '{}' attached to it."
                    self.stdout.write(msg.format(name))

            if isinstance(apphook, CatalogSearchCMSApp):
                required_apps.remove(CatalogSearchCMSApp)
                search_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if not search_pages.exists():
                    msg = "At least one CMS page should have an Application of type '{}' attached to it."
                    self.stdout.write(msg.format(name))

            if isinstance(apphook, OrderApp):
                required_apps.remove(OrderApp)
                order_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if not order_pages.exists():
                    msg = "At least one CMS page should have an Application of type '{}' attached to it."
                    self.stdout.write(msg.format(name))
