# -*- coding: utf-8
from __future__ import unicode_literals

import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from myshop.models.polymorphic.smartcard import SmartCard
from cmsplugin_cascade.models import CascadeElement


class CheckoutTest(TestCase):
    fixtures = ['myshop-polymorphic.json']

    def setUp(self):
        # add our sample item to the cart
        super(CheckoutTest, self).setUp()
        sample = SmartCard.objects.get(slug='sdhc-card-4gb')
        self.assertIsNotNone(sample)
        add2cart_url = sample.get_absolute_url() + '/add-to-cart'
        response = self.client.get(add2cart_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        payload = json.loads(response.content.decode('utf-8'))
        cart_url = reverse('shop:cart-list')
        payload['quantity'] = 1
        response = self.client.post(cart_url, payload)
        self.assertEqual(response.status_code, 201)

    def test_checkout_as_guest(self):
        continue_as_guest_url = reverse('shop:continue-as-guest')
        response = self.client.post(continue_as_guest_url)
        self.assertEqual(response.status_code, 200)
        print(response.content)

        checkout_upload_url = reverse('shop:checkout-upload')
        element = CascadeElement.objects.get(plugin_type='GuestFormPlugin', language='en',
                                             placeholder__page__publisher_is_draft=False)
        data = {'guest': {'email': "admin@example.com", 'plugin_id': element.pk, 'plugin_order': '1'}}
        response = self.client.post(checkout_upload_url)
        self.assertEqual(response.status_code, 200)

        print(response.content)
        print(response.cookies)
        self.fail()
