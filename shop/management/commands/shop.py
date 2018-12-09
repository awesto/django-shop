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

        complains = []

        # check for missing apphooks not registered by the merchant implementation
        required_apps = [CatalogListCMSApp, CatalogSearchCMSApp, OrderApp, PasswordResetApp]
        for apphook, _ in apphook_pool.get_apphooks():
            apphook = apphook_pool.get_apphook(apphook)
            for required_app in required_apps:
                if isinstance(apphook, required_app):
                    required_apps.remove(required_app)
                    break
        for missing_app in required_apps:
            msg = "The project must register an AppHook inheriting from '{}'"
            complains.push(msg.format(missing_app.__name__))

        # check for CMS pages requiring to be configured with an Application
        missing_page_msg = "At least one CMS page should have an Application of type '{}' attached to it."
        for apphook, name in apphook_pool.get_apphooks():
            apphook = apphook_pool.get_apphook(apphook)
            if isinstance(apphook, CatalogListCMSApp):
                catalog_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if not catalog_pages.exists():
                    complains.push(missing_page_msg.format(name))

            if isinstance(apphook, CatalogSearchCMSApp):
                search_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if search_pages.exists():
                    if not search_pages.filter(reverse_id='shop-search-product').exists():
                        msg = "A CMS page implementing the Search Application must be referenced with ID: 'shop-search-product'."
                        complains.push(msg)
                else:
                    complains.push(missing_page_msg.format(name))

            if isinstance(apphook, OrderApp):
                order_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if order_pages.exists():
                    if not order_pages.filter(reverse_id='shop-order').exists():
                        msg = "A CMS page implementing the Order Views must be referenced with ID: 'shop-order'."
                        complains.push(msg)
                    if not order_pages.filter(reverse_id='shop-order-last').exists():
                        msg = "A CMS page implementing the Thank You Order must be referenced with ID: 'shop-order-last'."
                        complains.push(msg)
                else:
                    complains.push(missing_page_msg.format(name))

            if isinstance(apphook, PasswordResetApp):
                password_reset_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
                if not password_reset_pages.exists():
                    complains.push(missing_page_msg.format(name))


        self.stdout.write(msg.format(name))
