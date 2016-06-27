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
        # from the product's detail page add our sample item to the cart
        add2cart_url = self.sample.get_absolute_url() + '/add-to-cart'
        response = self.client.get(add2cart_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.cookies.has_key('sessionid'))
        payload = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(payload, dict)
        self.assertDictContainsSubset(
            {'quantity': 1, 'unit_price': "€ 3.99", 'product': 1, 'extra': {'product_code': '1041'}},
            payload)

        # add two items of that Smart Card
        cart_url = reverse('shop:cart-list')
        payload['quantity'] = 2
        response = self.client.post(cart_url, payload)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.cookies.has_key('sessionid'))

        # examine if our product is in the cart
        cart = json.loads(response.content.decode('utf-8'))
        self.assertDictContainsSubset(
            {'id': self.sample.pk, 'product_name': "SDHC Card 4GB",
             'product_url': self.sample.get_absolute_url(), 'product_model': "smartcard",
             'price': "€ 3.99"},
            cart['summary'])

        response = self.client.get(cart_url)
        self.assertEqual(response.status_code, 200)
        cart = json.loads(response.content.decode('utf-8'))
        self.assertEqual(cart['num_items'], 1)
        self.assertEqual(cart['total_quantity'], 2)
        cart_item = cart['items'].pop()
        self.assertEqual(cart['total_quantity'], 2)

        # update quantity
        payload = {'product': self.sample.pk, 'quantity': 3, 'extra': 'product_code',
            'summary': {}, 'extra_rows': []}
        response = self.client.put(cart_item['url'], data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        cart_item = json.loads(response.content.decode('utf-8'))

        # reread the cart, and check quantity
        response = self.client.get(cart_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        cart = json.loads(response.content.decode('utf-8'))
        self.assertEqual(cart['total_quantity'], 3)

        # move that item to the watch-list
        payload['quantity'] = 0
        # print(payload)
        response = self.client.put(cart_item['url'], data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # reread the cart, and check quantity
        response = self.client.get(cart_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        cart = json.loads(response.content.decode('utf-8'))
        self.assertDictContainsSubset({'items': [], 'total_quantity': 0, 'num_items': 0, 'subtotal': "€ 0.00"}, cart)

        # check the watch-list
        watch_list_url = reverse('shop:watch-list')
        response = self.client.get(watch_list_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        watch_list = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(watch_list, dict)
        self.assertDictContainsSubset({'num_items': 0}, watch_list)
        self.assertEqual(len(watch_list['items']), 1)
        watch_item = watch_list['items'].pop()
        self.assertDictContainsSubset(
            {'product': self.sample.pk, 'quantity': 0, 'extra': 'product_code'}, watch_item)

        # move it back to the cart
        payload['quantity'] = 1
        response = self.client.put(watch_item['url'], data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # check that watch-list is empty
        response = self.client.get(watch_list_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(payload['items']), 0)

        # check that item is in the cart again
        response = self.client.get(cart_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        cart = json.loads(response.content.decode('utf-8'))
        self.assertEqual(cart['num_items'], 1)
        self.assertEqual(cart['total_quantity'], 1)
        cart_item = cart['items'].pop()
        self.assertDictContainsSubset({"product": self.sample.pk, 'quantity': 1,
            'extra': 'product_code'}, cart_item)
