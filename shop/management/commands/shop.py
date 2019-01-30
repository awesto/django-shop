# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string


class MissingPage(CommandError):
    """
    Exception class indicating that a CMS page with a predefined ``reverse_id`` is missing.
    """


class MissingAppHook(CommandError):
    """
    Exception class indicating that a page misses the application.
    """


class MissingPlugin(CommandError):
    """
    Exception class indicating that a special plugin is missing or misconfigured on a given
    CMS page.
    """


class Command(BaseCommand):
    help = "Commands for Django-SHOP."

    def add_arguments(self, parser):
        parser.add_argument(
            'subcommand',
            help="./manage.py shop [customers|check-pages]",
        )
        parser.add_argument(
            '--delete-expired',
            action='store_true',
            dest='delete_expired',
            help="Delete customers with expired sessions.",
        )
        parser.add_argument(
            '--add-missing',
            action='store_true',
            dest='add_missing',
            default=False,
            help="Use in combination with 'check-pages': Add missing pages.",
        )

    def handle(self, verbosity, subcommand, *args, **options):
        if subcommand == 'customers':
            self.delete_expired = options['delete_expired']
            self.customers()
        elif subcommand == 'check-pages':
            self.add_missing = options['add_missing']
            self.check_pages()
        else:
            msg = "Unknown sub-command for shop. Use one of: check-pages create-pages"
            self.stderr.write(msg.format(subcommand))


    def customers(self):
        """
        Entry point for subcommand ``./manage.py shop customers``.
        """
        from shop.models.customer import CustomerModel

        data = dict(total=0, anonymous=0, active=0, staff=0, guests=0, registered=0, expired=0)
        for customer in CustomerModel.objects.iterator():
            data['total'] += 1
            if customer.user.is_active:
                data['active'] += 1
            if customer.user.is_staff:
                data['staff'] += 1
            if customer.is_registered:
                data['registered'] += 1
            elif customer.is_guest:
                data['guests'] += 1
            elif customer.is_anonymous:
                data['anonymous'] += 1
            if customer.is_expired:
                data['expired'] += 1
                if self.delete_expired:
                    customer.delete()
        msg = "Customers in this shop: total={total}, anonymous={anonymous}, expired={expired}, active={active}, guests={guests}, registered={registered}, staff={staff}."
        self.stdout.write(msg.format(**data))

    def check_pages(self):
        """
        Entry point for subcommand ``./manage.py shop check-pages``.
        """
        from cms.models.pagemodel import Page

        complains = []
        apphook = self.get_installed_apphook('CatalogListCMSApp')
        catalog_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
        if not catalog_pages.exists():
            if self.add_missing:
                attribs = ("Catalog", '', apphook.__class__.__name__, 'ShopCatalogPlugin', {}),
                page = self.create_and_fill_page(*attribs)
                self.assign_all_products_to_page(page)
            else:
                msg = "There should be at least one published CMS page configured to use an Application inheriting from 'CatalogListCMSApp'."
                complains.append(msg)

        page_attributes = [
            ("Search", 'shop-search-product', 'CatalogSearchCMSApp', 'ShopSearchResultsPlugin', {}),
            ("Cart", 'shop-cart', None, 'ShopCartPlugin', {'render_type': 'editable'}),
            ("Watch-List", 'shop-watch-list', None, 'ShopCartPlugin', {'render_type': 'watch'}),
            ("Your Orders", 'shop-order', 'OrderApp', 'ShopOrderViewsPlugin', {}),
            ("Login", 'shop-login', None, 'ShopAuthenticationPlugin', {'form_type': 'login'}),
            ("Register Customer", 'shop-register-customer', None, 'ShopAuthenticationPlugin', {'form_type': 'register-user'}),
            ("Your Personal Details", 'shop-customer-details', None, 'CustomerFormPlugin', {}),
            ("Change Password", 'shop-password-change', None, 'ShopAuthenticationPlugin', {'form_type': 'password-change'}),
            ("Request Password Reset", 'password-reset-request', None, 'ShopAuthenticationPlugin', {'form_type': 'password-reset-request'}),
            ("Confirm Password Reset", 'password-reset-confirm', 'PasswordResetApp', 'ShopAuthenticationPlugin', {'form_type': 'password-reset-confirm'}),
        ]
        for attribs in page_attributes:
            try:
                self.check_page_content(*attribs)
            except MissingPage as exc:
                if self.add_missing:
                    self.create_and_fill_page(*attribs)
                else:
                    complains.append(str(exc))
            except CommandError as exc:
                complains.append(str(exc))

        if len(complains) > 0:
            rows = [" {}. {}".format(id, msg) for id, msg in enumerate(complains, 1)]
            rows.insert(0, "The following CMS pages must be fixed:")
            msg = "\n".join(rows)
            self.stdout.write(msg)

    def get_installed_apphook(self, base_apphook_name):
        from cms.apphook_pool import apphook_pool
        base_apphook = import_string('shop.cms_apphooks.' + base_apphook_name)

        for apphook, _ in apphook_pool.get_apphooks():
            apphook = apphook_pool.get_apphook(apphook)
            if isinstance(apphook, base_apphook):
                return apphook
        else:
            msg = "The project must register an AppHook inheriting from '{apphook_name}'"
            raise MissingAppHook(msg.format(apphook_name=base_apphook_name))

    def check_page_content(self, title, reverse_id, base_apphook_name, plugin_type, subset):
        from cms.apphook_pool import apphook_pool
        from cms.models.pagemodel import Page
        from cms.plugin_pool import plugin_pool

        page = Page.objects.public().filter(reverse_id=reverse_id).first()
        if not page:
            msg = "There should be a published CMS page with a reference ID: '{reverse_id}'."
            raise MissingPage(msg.format(reverse_id=reverse_id))

        if base_apphook_name:
            apphook = self.get_installed_apphook(base_apphook_name)
            if apphook_pool.get_apphook(page.application_urls) is not apphook:
                msg = "Page on URL '{url}' must be configured to use Application inheriting from '{app_hook}'."
                raise MissingAppHook(msg.format(url=page.get_absolute_url(), apphook_name=base_apphook_name))

        placeholder = page.placeholders.filter(slot='Main Content').first()
        if not placeholder:
            msg = "Page on URL '{url}' does not contain any plugin."
            raise MissingPlugin(msg.format(url=page.get_absolute_url()))

        plugin_name = plugin_pool.get_plugin(plugin_type).name
        for language in page.get_languages():
            plugin = placeholder.cmsplugin_set.filter(plugin_type=plugin_type, language=language).first()
            if not plugin:
                msg = "Page on URL '{url}' shall contain a plugin named '{plugin_name}'."
                raise MissingPlugin(msg.format(url=page.get_absolute_url(), plugin_name=plugin_name))

            glossary_items = plugin.get_bound_plugin().glossary.items()
            if not all(item in glossary_items for item in subset.items()):
                msg = "Plugin named '{plugin_name}' on page with URL '{url}' is misconfigured."
                raise MissingPlugin(msg.format(url=page.get_absolute_url(), plugin_name=plugin_name))

    def create_and_fill_page(self, title, reverse_id, base_apphook_name, plugin_type, subset):
        from cms.api import create_page, add_plugin, copy_plugins_to_language, create_title
        from cms.utils.i18n import get_public_languages

        template = settings.CMS_TEMPLATES[0][0]
        apphook = self.get_installed_apphook(base_apphook_name) if base_apphook_name else None
        languages = get_public_languages()
        page = create_page(title, template, languages[0], apphook,
                           created_by="manage.py shop check-pages",
                           reverse_id=reverse_id)
        placeholder = page.placeholders.get(slot='Main Content')
        data = {
            'glossary': {
                'breakpoints': ['xs', 'sm', 'md', 'lg', 'xl'],
                'fluid': None,
            }
        }
        container = add_plugin(placeholder, 'BootstrapContainerPlugin', languages[0], **data)
        row = add_plugin(placeholder, 'BootstrapRowPlugin', languages[0], target=container)
        data = {
            'glossary': {
                'xs-column-width': 'col',
            }
        }
        column = add_plugin(placeholder, 'BootstrapColumnPlugin', languages[0], target=row, **data)
        data = {
            'glossary': subset,
        }
        add_plugin(placeholder, plugin_type, languages[0], target=column, **data)
        page.publish(languages[0])
        for language in languages[1:]:
            create_title(language, title, page, menu_title=None)
            copy_plugins_to_language(page, languages[0], language)
            page.publish(language)
        return page

    def assign_all_products_to_page(self, page):
        from shop.models.product import ProductModel
        from shop.models.related import ProductPageModel

        for product in ProductModel.objects.all():
            ProductPageModel.objects.create(page=page, product=product)
