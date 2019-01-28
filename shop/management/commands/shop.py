# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    help = _("Collect information about all customers which accessed this shop.")

    def add_arguments(self, parser):
        parser.add_argument("subcommand", help="./manage.py shop [customers|check-pages]")
        parser.add_argument("--add-missing")

    def handle(self, verbosity, subcommand, *args, **options):
        if subcommand == 'check-pages':
            self.check_pages()
        else:
            msg = "Unknown sub-command for shop. Use one of: check-pages create-pages"
            self.stderr.write(msg.format(subcommand))

    def check_pages(self):
        from cms.models.pagemodel import Page

        complains = []
        apphook = self.get_installed_apphook('CatalogListCMSApp')
        catalog_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
        if not catalog_pages.exists():
            msg = "There should be at least one published CMS page configured to use an Application inheriting from 'CatalogListCMSApp'."
            complains.append(msg)

        page_attributes = [
            ('shop-search-product', 'CatalogSearchCMSApp', 'ShopSearchResultsPlugin', {}),
            ('shop-cart', None, 'ShopCartPlugin', {'render_type': 'editable'}),
            ('shop-watch-list', None, 'ShopCartPlugin', {'render_type': 'watch'}),
            ('shop-order', 'OrderApp', 'ShopOrderViewsPlugin', {}),
            ('shop-customer-details', None, 'CustomerFormPlugin', {}),
            ('shop-password-change', None, 'ShopAuthenticationPlugin', {'form_type': 'password-change'}),
            ('password-reset-request', None, 'ShopAuthenticationPlugin', {'form_type': 'password-reset-request'}),
            ('password-reset-confirm', 'PasswordResetApp', 'ShopAuthenticationPlugin', {'form_type': 'password-reset-confirm'}),
        ]
        for attribs in page_attributes:
            try:
                self.check_page_content(*attribs)
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

    def check_page_content(self, reverse_id, base_apphook_name, plugin_type, subset):
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
