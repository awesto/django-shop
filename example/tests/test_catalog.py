# -*- coding: utf-8
from __future__ import unicode_literals

import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from myshop.models.polymorphic.smartcard import SmartCard
from myshop.models import Cart


class CatalogTest(TestCase):
    fixtures = ['myshop-polymorphic.json']

    def setUp(self):
        super(CatalogTest, self).setUp()
        self.sample = SmartCard.objects.get(slug='sdhc-card-4gb')
        self.assertIsNotNone(self.sample)

    def skip_test_html_content(self):
        from bs4 import BeautifulSoup

        url = self.sample.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup.prettify())
        self.assertEqual(soup.title.string, 'SDHC Card 4GB')
        breadcrumb = soup.find('ol', class_='breadcrumb')
        list_items = breadcrumb.find_all('li')
        self.assertEqual(list_items[0].a.string, 'HOME')
        self.assertEqual(list_items[1].a.string, 'Shop')
        self.assertEqual(list_items[2].a.string, 'Smart Cards')
        active_item = breadcrumb.find('li', class_='active')
        self.assertEqual(active_item.string, 'SDHC Card 4GB')

    def test_add2cart(self):
        #
        url = self.sample.get_absolute_url() + '/add-to-cart'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        payload = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertDictContainsSubset(
            {'quantity': 1, 'unit_price': "€ 3.99", 'product': 1, 'extra': {'product_code': '1041'}},
            payload)

        # add two items of that Smart Card
        payload['quantity'] = 2
        url = reverse('shop:cart-list')
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)

        # examine if our product is in the cart
        cart = json.loads(response.content.decode('utf-8'))
        self.assertDictContainsSubset(
            {'id': 1, 'product_name': "SDHC Card 4GB", 'product_url': self.sample.get_absolute_url(),
             'product_model': "smartcard", 'price': "€ 3.99"},
            cart['summary'])

        # and add another one
        payload['quantity'] = 1
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)

        # now check the cart detail
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print(response.content)
        cart = json.loads(response.content.decode('utf-8'))
        self.assertDictContainsSubset({'num_items': 1, 'total_quantity': 3, 'subtotal': "€ 11.97",
            'extra_rows': [{'amount': "€ 1.91", 'modifier': "cartexcludedtaxmodifier",
                'label': "19% VAT incl."}], 'total': "€ 11.97"}, cart)
