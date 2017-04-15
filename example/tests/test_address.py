# -*- coding: utf-8
from __future__ import unicode_literals

import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework.test import APIClient, APITestCase, APIRequestFactory

from shop.models.defaults.cart import Cart
from shop.models.defaults.customer import Customer
from shop.models.defaults.address import ShippingAddress, BillingAddress


class AddressFormTest(APITestCase):
    def setUp(self):
        super(AddressFormTest, self).setUp()
        user = get_user_model().objects.create_user('lauren', 'lauren@example.com', 'secret')
        self.customer = Customer.objects.create(user=user)
        self.customer.is_staff = self.customer.is_superuser = False
        self.customer.save()
        self.client = APIClient()
        self.assertTrue(self.client.login(username='lauren', password='secret'))
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        request.customer = self.customer
        self.cart = Cart.objects.get_from_request(request)
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 0)
        self.assertEqual(BillingAddress.objects.filter(customer=self.customer).count(), 0)

    def test_add_first_shipping_address(self):
        shipping_address = {
            "name": "Lauren Callagar",
            "address1": "117, Lake St.",
            "zip_code": "CA 90066",
            "city": "Los Angeles",
            "country": "US",
        }
        url = reverse('shop:checkout-upload')

        # Lauren adds a shipping address but forgets to enter the city name
        payload = {
            "shipping_address": dict(shipping_address, city="", plugin_order='1', active_priority='add'),
            "billing_address": {
                "plugin_order": "2",
                "active_priority": "add",
                "use_primary_address": True,
            },
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertFalse(response['data']['$valid'])
        self.assertDictEqual({'city': ["This field is required."]},
                             response['errors']['shipping_address_form'])
        self.assertDictEqual(response['errors']['billing_address_form'], {})

        # Lauren adds the missing city and retries
        payload['shipping_address'] = dict(response['data']['shipping_address'], city="Los Angeles")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue(response['data']['$valid'])
        self.assertDictEqual({}, response['errors']['shipping_address_form'])
        self.assertDictEqual(response['errors']['billing_address_form'], {})
        self.assertEqual(response['checkout_summary']['shipping_address_form'],
                         "Lauren Callagar\n117, Lake St.\nCA 90066\nLos Angeles\nUnited States")
        self.assertEqual(response['checkout_summary']['billing_address_form'],
                         "Use shipping address for billing")

        # check the database's content
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 1)
        self.assertEqual(BillingAddress.objects.filter(customer=self.customer).count(), 0)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.shipping_address.as_text(),
                         "Lauren Callagar\n117, Lake St.\nCA 90066 Los Angeles\nUnited States\n")
        self.assertIsNone(self.cart.billing_address)

    def test_add_second_shipping_address(self):
        first_address = {
            "name": "Charles Smith",
            "address1": "507, Dudley St.",
            "zip_code": "PA 19148",
            "city": "Philadelphia",
            "country": "US",
        }
        second_address = {
            'name': "Charles Smith",
            'address1': "1012, Madison Ave",
            'city': "Baltimore",
            'zip_code': "MD 21201",
            'country': "US",
         }
        url = reverse('shop:checkout-upload')

        # Charles adds the first address
        payload = {
            'shipping_address': dict(first_address, plugin_order='1', active_priority='add'),
            'billing_address': {
                "plugin_order": "2",
                "active_priority": "add",
                "use_primary_address": True,
            },
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue(response['data']['$valid'])
        self.assertDictEqual(response['errors']['shipping_address_form'], {})
        self.assertDictEqual(response['errors']['billing_address_form'], {})
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 1)
        self.assertEqual(BillingAddress.objects.filter(customer=self.customer).count(), 0)

        # Charles add the second address
        payload['shipping_address'] = dict(second_address, plugin_order='1', active_priority='new')
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertDictContainsSubset({'active_priority': 'add'}, response['data']['shipping_address'])
        self.assertEqual("Use shipping address for billing",
                         response['checkout_summary']['billing_address_form'])
        payload['shipping_address'] = dict(response['data']['shipping_address'], **second_address)
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue(response['data']['$valid'])
        self.assertDictEqual(response['errors']['shipping_address_form'], {})
        self.assertDictEqual(response['errors']['billing_address_form'], {})
        self.assertEqual(response['checkout_summary']['shipping_address_form'],
                         "Charles Smith\n1012, Madison Ave\nMD 21201\nBaltimore\nUnited States")
        self.assertEqual(response['checkout_summary']['billing_address_form'],
                         "Use shipping address for billing")

        # check the database's content
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 2)
        self.assertEqual(BillingAddress.objects.filter(customer=self.customer).count(), 0)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.shipping_address.as_text(),
                         "Charles Smith\n1012, Madison Ave\nMD 21201 Baltimore\nUnited States\n")
        self.assertIsNone(self.cart.billing_address)

        print(self.cart.shipping_address_id)

        # Charles selects its first address in Philadelphia
        payload['shipping_address'] = dict(response['data']['shipping_address'], active_priority='1')
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue(response['data']['$valid'])
        self.cart.refresh_from_db()
        print(self.cart.shipping_address_id)
        self.assertEqual(self.cart.shipping_address.as_text(),
                         "Charles Smith\n507, Dudley St.\nPA 19148 Philadelphia\nUnited States\n")
