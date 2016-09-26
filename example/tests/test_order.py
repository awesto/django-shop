# -*- coding: utf-8
from __future__ import unicode_literals

import json
from django.core.urlresolvers import reverse
from cms.api import add_plugin, create_page
from bs4 import BeautifulSoup
from shop.cascade.checkout import GuestFormPlugin

from .test_shop import ShopTestCase

class CheckoutTest(ShopTestCase):
    def setUp(self):
        # add our sample item to the cart
        super(CheckoutTest, self).setUp()

        # create a page populated with Cascade elements used for checkout
        self.checkout_page = create_page("Checkout", 'INHERIT', 'en', parent=self.home_page,
                                    published=True, in_navigation=True)

    def add_guestform_element(self):
        """Add one GuestFormPlugin to the current page"""
        column_element = self.create_page_grid(self.checkout_page)
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')
        guestform_element = add_plugin(placeholder, GuestFormPlugin, 'en', target=column_element)
        self.checkout_page.publish('en')
        return guestform_element

    def test_checkout_as_guest(self):
        guestform_element = self.add_guestform_element()

        self.add_product2cart()
        continue_as_guest_url = reverse('shop:continue-as-guest')
        response = self.client.post(continue_as_guest_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.checkout_page.get_absolute_url())
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content)
        # soup.prettify()
        # TODO: check for form

        data = {'guest': {'email': "admin@example.com", 'plugin_id': guestform_element.pk,
                'plugin_order': '1'}}

        checkout_upload_url = reverse('shop:checkout-upload')
        response = self.client.post(checkout_upload_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
