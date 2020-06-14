from cms.models.static_placeholder import StaticPlaceholder
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string
from cmsplugin_cascade.models import CascadeClipboard
from shop.management.utils import deserialize_to_placeholder


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
            help="./manage.py shop [customers|check-pages|review-settings]",
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
            help="Use in combination with 'check-pages' to add missing mandatory pages.",
        )
        parser.add_argument(
            '--add-recommended',
            action='store_true',
            dest='add_recommended',
            default=False,
            help="Use in combination with 'check-pages' to add missing recommended pages.",
        )

    def handle(self, verbosity, subcommand, *args, **options):
        if subcommand == 'help':
            self.stdout.write("""
Usage:

./manage.py shop customers
    Show how many customers are registered, guests, anonymous or expired.            
    Use option --delete-expired to delete all customers with an expired session.            

./manage.py shop check-pages
    Iterate over all pages in the CMS and check, if they are properly configured.
    Use option --add-missing to add all missing mandatory pages for this shop.
    Use option --add-recommended to also add missing but recommended pages for this shop.

./manage.py shop review-settings
    Review all shop related settings and complain about missing- or mis-configurations.
""")
        elif subcommand == 'customers':
            self.delete_expired = options['delete_expired']
            self.customers()
        elif subcommand == 'check-pages':
            self.stdout.write("The following CMS pages must be adjusted:")
            self.add_recommended = options['add_recommended']
            self.add_mandatory = options['add_missing'] or self.add_recommended
            self.personal_pages = self.impersonal_pages = None
            if self.add_recommended:
                for k, msg in enumerate(self.create_recommended_pages(), 1):
                    self.stdout.write(" {}. {}".format(k, msg))
            for k, msg in enumerate(self.check_mandatory_pages(), 1):
                self.stdout.write(" {}. {}".format(k, msg))
        elif subcommand == 'review-settings':
            self.stdout.write("The following configuration settings must be fixed:")
            for k, msg in enumerate(self.review_settings(), 1):
                self.stdout.write(" {}. {}".format(k, msg))
        else:
            msg = "Unknown sub-command for shop. Use one of: customer check-pages review-settings"
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
                if self.delete_expired and customer.orders.count() == 0:
                    customer.delete()
        msg = "Customers in this shop: total={total}, anonymous={anonymous}, expired={expired}, active={active}, guests={guests}, registered={registered}, staff={staff}."
        self.stdout.write(msg.format(**data))

    def create_recommended_pages(self):
        from cms.models.pagemodel import Page
        from cms.utils.i18n import get_public_languages

        default_language = get_public_languages()[0]

        # create the HOME page
        if Page.objects.public().filter(is_home=True).exists():
            yield "A home page exists already."
        else:
            page, created = self.get_or_create_page("Home", None, in_navigation=True)
            assert created is True
            try:
                clipboard = CascadeClipboard.objects.get(identifier='home')
            except CascadeClipboard.DoesNotExist:
                pass
            else:
                self.deserialize_to_placeholder(page, clipboard.data)
            try:
                clipboard = CascadeClipboard.objects.get(identifier='footer')
            except CascadeClipboard.DoesNotExist:
                pass
            else:
                static_placeholder = StaticPlaceholder.objects.create(code='Static Footer')
                deserialize_to_placeholder(static_placeholder.public, clipboard.data, default_language)
                deserialize_to_placeholder(static_placeholder.draft, clipboard.data, default_language)
            page.set_as_homepage()
            self.publish_in_all_languages(page)
            yield "Created recommended CMS home page."

        parent_page, created = self.get_or_create_page("Legal", None, reverse_id='shop-legal-pages', soft_root=True)
        if created:
            self.publish_in_all_languages(parent_page)
            yield "Created recommended CMS page 'Legal'."
        else:
            yield "Recommended CMS page 'Legal' exists already."

        page, created = self.get_or_create_page("Imprint", None, parent_page=parent_page, in_navigation=True)
        if created:
            self.publish_in_all_languages(page)
            yield "Created recommended CMS page 'Imprint'."
        else:
            yield "Recommended CMS page 'Imprint' exists already."

        page, created = self.get_or_create_page("Terms and Conditions", None, parent_page=parent_page, in_navigation=True)
        if created:
            self.publish_in_all_languages(page)
            yield "Created recommended CMS page 'Terms and Conditions'."
        else:
            yield "Recommended CMS page 'Terms and Conditions' exists already."

        page, created = self.get_or_create_page("Privacy Protection", None, parent_page=parent_page, in_navigation=True)
        if created:
            self.publish_in_all_languages(page)
            yield "Created recommended CMS page 'Privacy Protection'."
        else:
            yield "Recommended CMS page 'Privacy Protection' exists already."

        self.personal_pages, created = self.get_or_create_page("Personal Pages", None, reverse_id='shop-personal-pages', soft_root=True)
        if created:
            self.publish_in_all_languages(self.personal_pages)
            yield "Created recommended CMS page 'Personal Pages'."
        else:
            yield "Recommended CMS page 'Personal Pages' exists already."

        self.impersonal_pages, created = self.get_or_create_page("Join Us", None, reverse_id='shop-impersonal-pages', soft_root=True)
        if created:
            self.publish_in_all_languages(self.impersonal_pages)
            yield "Created recommended CMS page 'Join Us'."
        else:
            yield "Recommended CMS page 'Join Us' exists already."

        try:
            apphook = self.get_installed_apphook('CatalogSearchApp')
        except MissingAppHook:
            yield "Unable to create recommended CMS page 'Search', because django-elasticsearch-dsl is not installed."
        else:
            page, created = self.get_or_create_page("Search", apphook=apphook, reverse_id='shop-search-product')
            if created:
                try:
                    clipboard = CascadeClipboard.objects.get(identifier=page.get_slug(default_language))
                except CascadeClipboard.DoesNotExist:
                    pass
                else:
                    self.deserialize_to_placeholder(page, clipboard.data)
                self.create_breadcrumb(page, {'render_type': 'catalog'})
                self.publish_in_all_languages(page)
                yield "Created recommended CMS page 'Search'."
            else:
                yield "Recommended CMS page 'Search' exists already."

    def check_mandatory_pages(self):
        """
        Entry point for subcommand ``./manage.py shop check-pages``.
        """
        from cms.models.pagemodel import Page
        from cms.models.pluginmodel import CMSPlugin
        from cms.utils.i18n import get_public_languages

        self._created_cms_pages = []
        default_language = get_public_languages()[0]

        # check for catalog pages
        apphook = self.get_installed_apphook('CatalogListCMSApp')
        catalog_pages = Page.objects.public().filter(application_urls=apphook.__class__.__name__)
        if not catalog_pages.exists():
            if self.add_mandatory:
                page, created = self.get_or_create_page("Catalog", apphook, in_navigation=True)
                if created:
                    try:
                        clipboard = CascadeClipboard.objects.get(identifier='shop-list')
                        self.deserialize_to_placeholder(page, clipboard.data)
                    except CascadeClipboard.DoesNotExist:
                        leaf_plugin = self.create_page_structure(page)
                        self.add_plugin(leaf_plugin, 'ShopCatalogPlugin', {})
                    self.create_breadcrumb(page, {'render_type': 'catalog'})
                    self.publish_in_all_languages(page)
                    self.assign_all_products_to_page(page)
                    yield "Created CMS page titled 'Catalog'."
                else:
                    yield "CMS page 'Catalog' exists already."
            else:
                yield "There should be at least one published CMS page configured to use an Application inheriting from 'CatalogListCMSApp'."

        page_scaffold = [
            # Menu Title, CMS-App-Hook or None, kwargs, Main Plugin, Plugin Context,
            ("Cart",
             {'reverse_id': 'shop-cart'},
             ('ShopCartPlugin', {'render_type': 'editable'}),
             {'render_type': 'soft-root'}),
            ("Watch-List",
             {'reverse_id': 'shop-watch-list'},
             ('ShopCartPlugin', {'render_type': 'watch'}),
             {'render_type': 'soft-root'}),
            ("Your Orders",
             {'apphook': self.get_installed_apphook('OrderApp'), 'reverse_id': 'shop-order', 'parent_page': self.personal_pages, 'in_navigation': True},
             ('ShopOrderViewsPlugin', {}),
             {'render_type': 'default'}),
            ("Personal Details",
             {'reverse_id': 'shop-customer-details', 'parent_page': self.personal_pages, 'in_navigation': True},
             ('CustomerFormPlugin', {}),
             {'render_type': 'default'}),
            ("Change Password",
             {'reverse_id': 'shop-password-change', 'parent_page': self.personal_pages, 'in_navigation': True},
             ('ShopAuthenticationPlugin', {'form_type': 'password-change'}),
             {'render_type': 'default'}),
            ("Login",
             {'reverse_id': 'shop-login', 'parent_page': self.impersonal_pages, 'in_navigation': True},
             ('ShopAuthenticationPlugin', {'form_type': 'login'}),
             {'render_type': 'default'}),
            ("Register Customer",
             {'reverse_id': 'shop-register-customer', 'parent_page': self.impersonal_pages, 'in_navigation': True},
             ('ShopAuthenticationPlugin', {'form_type': 'register-user'}),
             {'render_type': 'default'}),
            ("Request Password Reset",
             {'reverse_id': 'password-reset-request', 'parent_page': self.impersonal_pages, 'in_navigation': True},
             ('ShopAuthenticationPlugin', {'form_type': 'password-reset-request'}),
             {'render_type': 'default'}),
            ("Confirm Password Reset",
             {'apphook': self.get_installed_apphook('PasswordResetApp'), 'reverse_id': 'password-reset-confirm'},
             ('ShopAuthenticationPlugin', {'form_type': 'password-reset-confirm'}),
             {'render_type': 'default'}),
            ("Payment Canceled",
             {'reverse_id': 'shop-cancel-payment'},
             ('HeadingPlugin', {'tag_type': "h2", 'content': "Your payment has been canceled"}),
             {'render_type': 'default'}),
        ]
        for page_title, page_attrs, content_attrs, breadcrumb_glossary in page_scaffold:
            try:
                page = self.check_page(page_title, **page_attrs)
                self.check_page_content(page, *content_attrs)
            except MissingPage as exc:
                if self.add_mandatory:
                    page, created = self.get_or_create_page(page_title, **page_attrs)
                    if created:
                        try:
                            clipboard = CascadeClipboard.objects.get(identifier=page.get_slug(default_language))
                            self.deserialize_to_placeholder(page, clipboard.data)
                        except CascadeClipboard.DoesNotExist:
                            leaf_plugin = self.create_page_structure(page)
                            self.add_plugin(leaf_plugin, *content_attrs)
                        if breadcrumb_glossary:
                            self.create_breadcrumb(page, breadcrumb_glossary)
                        self.publish_in_all_languages(page)
                        yield "Created mandatory CMS page titled '{0}'.".format(page.get_title(default_language))
                    else:
                        yield "Mandatory CMS page '{0}' exists already.".format(page.get_title(default_language))
                else:
                    yield str(exc)
            except CommandError as exc:
                yield str(exc)

        # the checkout page must be found through the purchase button
        for plugin in CMSPlugin.objects.filter(plugin_type='ShopProceedButton', language=default_language, placeholder__page__publisher_is_draft=False):
            link = plugin.get_bound_plugin().glossary.get('link')
            if isinstance(link, dict) and link.get('type') == 'PURCHASE_NOW':
                break
        else:
            if self.add_mandatory:
                page, created = self.get_or_create_page("Checkout", None)
                if created:
                    try:
                        clipboard = CascadeClipboard.objects.get(identifier='checkout')
                        self.deserialize_to_placeholder(page, clipboard.data)
                    except CascadeClipboard.DoesNotExist:
                        column_plugin = self.create_page_structure(page)
                        forms_plugin = self.add_plugin(column_plugin, 'ValidateSetOfFormsPlugin', {})
                        glossary = {'button_type': 'btn-success', 'link': {'type': 'PURCHASE_NOW'}, 'link_content': "Purchase Now"}
                        self.add_plugin(forms_plugin, 'ShopProceedButton', glossary)
                    self.publish_in_all_languages(page)
                    yield "Created CMS page titled 'Checkout'"
                else:
                    yield "CMS page titled 'Checkout' exists already."
            else:
                yield "There should be at least one published CMS page containing a 'Proceed Button Plugin' for purchasing the cart's content."

    @classmethod
    def get_installed_apphook(cls, base_apphook_name):
        from cms.apphook_pool import apphook_pool
        base_apphook = import_string('shop.cms_apphooks.' + base_apphook_name)

        for apphook, _ in apphook_pool.get_apphooks():
            apphook = apphook_pool.get_apphook(apphook)
            if isinstance(apphook, base_apphook):
                return apphook
        else:
            msg = "The project must register an AppHook inheriting from '{apphook_name}'"
            raise MissingAppHook(msg.format(apphook_name=base_apphook_name))

    def check_page(self, title, apphook=None, reverse_id=None, **kwargs):
        from cms.models.pagemodel import Page
        from cms.apphook_pool import apphook_pool

        page = Page.objects.public().filter(reverse_id=reverse_id).first()
        if not page:
            msg = "There should be a published CMS page with a reference ID: '{reverse_id}'."
            raise MissingPage(msg.format(reverse_id=reverse_id))

        if apphook:
            if not page.application_urls or apphook_pool.get_apphook(page.application_urls) is not apphook:
                msg = "Page on URL '{url}' must be configured to use CMSApp inheriting from '{apphook}'."
                raise MissingAppHook(msg.format(url=page.get_absolute_url(), apphook=apphook.__class__))

        return page

    def check_page_content(self, page, plugin_type, subset):
        from cms.plugin_pool import plugin_pool

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

    def get_or_create_page(self, title, apphook=None, reverse_id=None, parent_page=None, in_navigation=False, soft_root=False):
        from cms.api import create_page
        from cms.models.pagemodel import Page
        from cms.utils.i18n import get_public_languages

        template = settings.CMS_TEMPLATES[0][0]
        language = get_public_languages()[0]
        try:
            parent_node = parent_page.node if parent_page else None
            page = Page.objects.drafts().get(
                reverse_id=reverse_id,
                node__parent=parent_node,
                title_set__title=title,
                title_set__language=language,
            )
            created = False
        except Page.DoesNotExist:
            page = create_page(
                title,
                template,
                language,
                apphook=apphook,
                created_by="manage.py shop check-pages",
                in_navigation=in_navigation,
                soft_root=soft_root,
                parent=parent_page,
                reverse_id=reverse_id,
            )
            created = True
        return page, created

    def create_page_structure(self, page, slot='Main Content'):
        from cms.api import add_plugin
        from cms.utils.i18n import get_public_languages

        placeholder = page.placeholders.get(slot=slot)
        language = get_public_languages()[0]
        glossary = {
            'breakpoints': ['xs', 'sm', 'md', 'lg', 'xl'],
            'fluid': None,
        }
        container = add_plugin(placeholder, 'BootstrapContainerPlugin', language, glossary=glossary)
        row = add_plugin(placeholder, 'BootstrapRowPlugin', language, target=container)
        glossary = {
            'xs-column-width': 'col',
        }
        return add_plugin(placeholder, 'BootstrapColumnPlugin', language, target=row, glossary=glossary)

    def create_breadcrumb(self, page, glossary, slot='Breadcrumb'):
        from cms.api import add_plugin
        from cms.utils.i18n import get_public_languages

        placeholder = page.placeholders.get(slot=slot)
        language = get_public_languages()[0]
        return add_plugin(placeholder, 'BreadcrumbPlugin', language, glossary=glossary)

    def add_plugin(self, leaf_plugin, plugin_type, glossary):
        from cms.api import add_plugin
        if plugin_type:
            return add_plugin(leaf_plugin.placeholder, plugin_type, leaf_plugin.language, target=leaf_plugin, glossary=glossary)

    @classmethod
    def publish_in_all_languages(cls, page):
        from cms.api import copy_plugins_to_language, create_title
        from cms.utils.i18n import get_public_languages

        languages = get_public_languages()
        for language in languages[1:]:
            create_title(language, page.get_title(), page, menu_title=None)
            copy_plugins_to_language(page, languages[0], language)
        for language in languages:
            page.publish(language)

    def assign_all_products_to_page(self, page):
        from shop.models.product import ProductModel
        from shop.models.related import ProductPageModel

        for product in ProductModel.objects.all():
            ProductPageModel.objects.create(page=page, product=product)

    def review_settings(self):
        from django.conf import settings

        if getattr(settings, 'AUTH_USER_MODEL', None) != 'email_auth.User':
            yield "settings.AUTH_USER_MODEL should be 'email_auth.User'."

        AUTHENTICATION_BACKENDS = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        if 'allauth.account.auth_backends.AuthenticationBackend' not in AUTHENTICATION_BACKENDS:
            yield "settings.AUTHENTICATION_BACKENDS should contain 'allauth.account.auth_backends.AuthenticationBackend'."

        if 'sass_processor.finders.CssFinder' not in getattr(settings, 'STATICFILES_FINDERS', []):
            yield "settings.STATICFILES_FINDERS should contain 'sass_processor.finders.CssFinder'."

        if 'node_modules' not in dict(getattr(settings, 'STATICFILES_DIRS', [])).keys():
            yield "settings.STATICFILES_DIRS should contain ('node_modules', '/…/node_modules')."

        if '/node_modules/' not in getattr(settings, 'NODE_MODULES_URL', ''):
            yield "settings.NODE_MODULES_URL should start with a URL pointing onto /…/node_modules/."

        for template_engine in getattr(settings, 'TEMPLATES', []):
            if template_engine['BACKEND'] != 'django.template.backends.django.DjangoTemplates':
                continue
            context_processors = template_engine['OPTIONS'].get('context_processors', [])
            if 'shop.context_processors.customer' not in context_processors:
                yield "'shop.context_processors.customer' is missing in 'context_processors' of the default Django Template engine."
            if 'shop.context_processors.shop_settings' not in context_processors:
                yield "'shop.context_processors.shop_settings' is missing in 'context_processors' of the default Django Template engine."
        for template_engine in getattr(settings, 'TEMPLATES', []):
            if template_engine['BACKEND'] == 'post_office.template.backends.post_office.PostOfficeTemplates':
                break
        else:
            yield "In settings.TEMPLATES, the backend for 'post_office.template.backends.post_office.PostOfficeTemplates' is missing."

        if getattr(settings, 'POST_OFFICE', {}).get('TEMPLATE_ENGINE') != 'post_office':
            yield "settings.POST_OFFICE should contain {'TEMPLATE_ENGINE': 'post_office'}."

        for dir in getattr(settings, 'SASS_PROCESSOR_INCLUDE_DIRS', []):
            if '/node_modules' in dir:
                break
        else:
            yield "settings.SASS_PROCESSOR_INCLUDE_DIRS should include the folder '…/node_modules'."

        if getattr(settings, 'COERCE_DECIMAL_TO_STRING', None) is not True:
            yield "settings.COERCE_DECIMAL_TO_STRING should be set to 'True'."

        if getattr(settings, 'FSM_ADMIN_FORCE_PERMIT', None) is not True:
            yield "settings.FSM_ADMIN_FORCE_PERMIT should be set to 'True'."

        if getattr(settings, 'SERIALIZATION_MODULES', {}).get('json') != 'shop.money.serializers':
            yield "settings.SERIALIZATION_MODULES['json'] should be set to 'shop.money.serializers'."

        REST_FRAMEWORK = getattr(settings, 'REST_FRAMEWORK', {})
        if 'shop.rest.money.JSONRenderer' not in REST_FRAMEWORK.get('DEFAULT_RENDERER_CLASSES', []):
            yield "settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] should contain class 'shop.rest.money.JSONRenderer'."

        if 'django_filters.rest_framework.DjangoFilterBackend' not in REST_FRAMEWORK.get('DEFAULT_FILTER_BACKENDS', []):
            yield "settings.REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS'] should contain class 'django_filters.rest_framework.DjangoFilterBackend'."

        if getattr(settings, 'REST_AUTH_SERIALIZERS', {}).get('LOGIN_SERIALIZER') != 'shop.serializers.auth.LoginSerializer':
            yield "settings.REST_AUTH_SERIALIZERS['LOGIN_SERIALIZER'] should be set to 'shop.serializers.auth.LoginSerializer'."

        if 'shop.cascade' not in getattr(settings, 'CMSPLUGIN_CASCADE_PLUGINS', []):
            yield "settings.CMSPLUGIN_CASCADE_PLUGINS should contain entry 'shop.cascade'."

        CMSPLUGIN_CASCADE = getattr(settings, 'CMSPLUGIN_CASCADE', {})
        if CMSPLUGIN_CASCADE.get('link_plugin_classes') != [
            'shop.cascade.plugin_base.CatalogLinkPluginBase',
            'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
            'shop.cascade.plugin_base.CatalogLinkForm']:
            yield "settings.CMSPLUGIN_CASCADE['link_plugin_classes'] should contain special classes able to link onto products."
        if CMSPLUGIN_CASCADE.get('bootstrap4', {}).get('template_basedir') != 'angular-ui':
            yield "settings.CMSPLUGIN_CASCADE['bootstrap4']['template_basedir'] should be 'angular-ui'."
        if CMSPLUGIN_CASCADE.get('segmentation_mixins') != [
            ('shop.cascade.segmentation.EmulateCustomerModelMixin',
             'shop.cascade.segmentation.EmulateCustomerAdminMixin')]:
            yield "settings.CMSPLUGIN_CASCADE['segmentation_mixins'] should contain a special version handling the Customer model."

        if not isinstance(getattr(settings, 'SHOP_CART_MODIFIERS', None), (list, tuple)):
            yield "settings.SHOP_CART_MODIFIERS should contain a list with cart modifiers."

    def deserialize_to_placeholder(self, page, data, slot='Main Content'):
        from cms.utils.i18n import get_public_languages

        language = get_public_languages()[0]
        placeholder = page.placeholders.get(slot=slot)
        deserialize_to_placeholder(placeholder, data, language)
