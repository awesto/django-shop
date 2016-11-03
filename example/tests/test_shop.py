# -*- coding: utf-8
from __future__ import unicode_literals

import json
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.test import TestCase, RequestFactory
from cms.api import add_plugin, create_page
from cmsplugin_cascade.bootstrap3 import settings as bs3_settings
from cmsplugin_cascade.bootstrap3.container import (BootstrapContainerPlugin, BootstrapRowPlugin,
                                                    BootstrapColumnPlugin)
from shop.middleware import CustomerMiddleware
from shop.money import Money
from shop.models.defaults.mapping import ProductPage
from shop.models.customer import CustomerState
from shop.models.defaults.customer import Customer

from myshop.models.polymorphic.smartcard import SmartCard
from myshop.models.manufacturer import Manufacturer
from myshop.cms_apps import ProductsListApp


class ShopTestCase(TestCase):
    def setUp(self):
        super(ShopTestCase, self).setUp()
        self.factory = RequestFactory()
        self.admin_site = admin.sites.AdminSite()
        self.create_pages()
        self.create_products()
        self.create_customers()

    def create_pages(self):
        self.home_page = create_page("HOME", 'myshop/pages/default.html', 'en', published=True,
                                     in_navigation=True)
        self.shop_page = create_page("Shop", 'INHERIT', 'en', parent=self.home_page, published=True,
                                     in_navigation=True, apphook=ProductsListApp)
        self.smartcards_page = create_page("Smart Cards", 'INHERIT', 'en', parent=self.shop_page,
                                           published=True, in_navigation=True, apphook=ProductsListApp)

    def create_products(self):
        manufacturer = Manufacturer.objects.create(name="SanDisk")
        sdhc_4gb = SmartCard.objects.create(
            product_name="SDHC Card 4GB",
            slug="sdhc-card-4gb",
            unit_price=Money('3.99'),
            caption="Dependability and solid performance",
            manufacturer=manufacturer,
            card_type="SDHC",
            storage=4,
            speed=4,
            product_code="sd1041",
            description="SanDisk SDHC and SDXC memory cards are great",
            order=1
        )
        ProductPage.objects.create(page=self.shop_page, product=sdhc_4gb)
        ProductPage.objects.create(page=self.smartcards_page, product=sdhc_4gb)

        xtr_sdhc_16gb = SmartCard.objects.create(
            product_name="EXTREME PLUS SDHC 16GB",
            slug="extreme-plus-sdhc-16gb",
            unit_price=Money('8.49'),
            caption="Up to 80/60MB/s read/write speed",
            manufacturer=manufacturer,
            card_type="SDHC",
            storage=16,
            speed=80,
            product_code="sd2016",
            description="SanDisk Extreme memory cards offer speed, capacity, and durability",
            order=2,
        )
        ProductPage.objects.create(page=self.shop_page, product=xtr_sdhc_16gb)
        ProductPage.objects.create(page=self.smartcards_page, product=xtr_sdhc_16gb)

        sdxc_pro_32gb = SmartCard.objects.create(
            product_name="Extreme PRO microSDHC 32GB",
            slug="extreme-pro-micro-sdhc-32gb",
            unit_price=Money('12.99'),
            caption="Up to 80/60MB/s read/write speed",
            manufacturer=manufacturer,
            card_type="SDXC",
            storage=32,
            speed=80,
            product_code="sd2018",
            description="SanDisk Extreme PRO microSDHC/microSDXC cards now come with up to 64GB",
            order=3,
        )
        ProductPage.objects.create(page=self.shop_page, product=sdxc_pro_32gb)
        ProductPage.objects.create(page=self.smartcards_page, product=sdxc_pro_32gb)

    def create_customers(self):
        BART = {
            'first_name': 'Bart',
            'last_name': 'Simpson',
            'email': 'bart@thesimpsons.com',
            'password': 'trab',
        }
        bart = get_user_model().objects.create_user('bart', **BART)
        bart = Customer.objects.create(user=bart, salutation='mr',
                                       recognized=CustomerState.REGISTERED)
        self.assertTrue(bart.is_registered())

    def add_product2cart(self, product):
        add2cart_url = product.get_absolute_url() + '/add-to-cart'
        response = self.client.get(add2cart_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content.decode('utf-8'))

        # add two items of that Smart Card
        cart_url = reverse('shop:cart-list')
        payload['quantity'] = 1
        response = self.client.post(cart_url, payload)
        self.assertEqual(response.status_code, 201)

    def create_page_grid(self, page):
        """
        With Cascade, create a Bootstrap Container, with a Row and a Column to be used as
        placeholder for all kinds of elements.
        """
        # locate placeholder
        placeholder = page.placeholders.get(slot='Main Content')

        # create container
        BS3_BREAKPOINT_KEYS = list(
            tp[0] for tp in bs3_settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])
        container_element = add_plugin(placeholder, BootstrapContainerPlugin, 'en',
                                       glossary={'breakpoints': BS3_BREAKPOINT_KEYS})
        container_plugin = container_element.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(container_plugin, BootstrapContainerPlugin)

        # add one row
        row_element = add_plugin(placeholder, BootstrapRowPlugin, 'en', target=container_element,
                                 glossary={})
        row_plugin = row_element.get_plugin_class_instance()
        self.assertIsInstance(row_plugin, BootstrapRowPlugin)

        # add one column
        column_element = add_plugin(placeholder, BootstrapColumnPlugin, 'en', target=row_element,
                                    glossary={'xs-column-width': 'col-xs-12',
                                              'sm-column-width': 'col-sm-6',
                                              'md-column-width': 'col-md-4',
                                              'lg-column-width': 'col-lg-3'})
        column_plugin = column_element.get_plugin_class_instance()
        self.assertIsInstance(column_plugin, BootstrapColumnPlugin)
        return column_element

    def middleware_process_request(self, request, sessionid=None):
        if sessionid:
            request.COOKIES[settings.SESSION_COOKIE_NAME] = sessionid
        SessionMiddleware().process_request(request)
        AuthenticationMiddleware().process_request(request)
        CustomerMiddleware().process_request(request)
