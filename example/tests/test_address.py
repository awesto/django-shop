# -*- coding: utf-8
from __future__ import unicode_literals

import json

from django import VERSION as DJANGO_VERSION
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
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue('shipping_address_form' in response)
        self.assertDictEqual({'city': ["This field is required."]},
                             response['shipping_address_form'])
        self.assertTrue('billing_address_form' in response)
        self.assertDictEqual(response['billing_address_form'], {})

        # Lauren adds the missing city and retries
        payload['shipping_address'].update(city="Los Angeles")
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue('shipping_address_form' in response)
        self.assertListEqual(
            response['shipping_address_form']['siblings_summary'],
            [{'value': '1', 'label': '1. Lauren Callagar – 117, Lake St. – CA 90066 Los Angeles – United States'}])

        self.assertTrue('billing_address_form' in response)
        self.assertTrue(response['billing_address_form']['use_primary_address'])
        self.assertEqual(response['billing_address_form']['active_priority'], 'add')

        # check the database's content
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 1)
        self.assertEqual(BillingAddress.objects.filter(customer=self.customer).count(), 0)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.shipping_address.as_text(),
                         "Lauren Callagar\n117, Lake St.\nCA 90066 Los Angeles\nUnited States\n")
        self.assertIsNone(self.cart.billing_address)

        # add the same address a second time and check that it's not duplicated
        # edit_address_url = reverse('shop:edit-shipping-address', kwargs={'priority':'add'})
        # response = self.client.put(url, payload, format='json')
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 1)
        # self.assertEqual(BillingAddress.objects.filter(customer=self.customer).count(), 0)

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

        edit_address_url = reverse('shop:edit-shipping-address', kwargs={'priority':'add'})
        response = self.client.get(edit_address_url)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertDictEqual(response['shipping_address_form'],
                            {'city': None, 'name': None, 'address1': None, 'address2': None, 'country': None, 'zip_code': None})

        # Charles adds the first address
        payload = {'shipping_address': dict(first_address, plugin_order='1', active_priority='add')}
        payload['shipping_address'].pop('city')  # forgot to fill out city
        response = self.client.put(edit_address_url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        response = json.loads(response.content.decode('utf-8'))
        self.assertDictEqual(response.pop('shipping_address_form'), {'errors': {u'city': [u'This field is required.']}})

        payload = {'shipping_address': dict(first_address, plugin_order='1', active_priority='add')}
        response = self.client.put(edit_address_url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 0)

        # associate that address with the current cart
        url = reverse('shop:checkout-upload')
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 1)

        # Charles adds the second address
        payload['shipping_address'] = dict(second_address, plugin_order='1', active_priority='add')
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        siblings_summary = response['shipping_address_form'].pop('siblings_summary')
        self.assertListEqual(siblings_summary, [
            {"value":"1","label":"1. Charles Smith – 507, Dudley St. – PA 19148 Philadelphia – United States"},
            {"value":"2","label":"2. Charles Smith – 1012, Madison Ave – MD 21201 Baltimore – United States"}
        ])
        self.assertEqual(response['shipping_address_form'].pop('active_priority'), '2')
        self.assertEqual(response['shipping_address_form'].pop('plugin_order'), '1')
        self.assertDictEqual(response['shipping_address_form'], second_address)
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 2)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.shipping_address.as_text(),
                         "Charles Smith\n1012, Madison Ave\nMD 21201 Baltimore\nUnited States\n")
        self.assertIsNone(self.cart.billing_address)

        # check that Charles selected the second address
        self.assertEqual(str(self.cart.shipping_address.priority), siblings_summary[1]['value'])
        empty_field = None if DJANGO_VERSION >= (1, 11) else ''

        # Charles selects his first address in Philadelphia
        active_priority = siblings_summary[0]['value']
        edit_address_url = reverse('shop:edit-shipping-address', kwargs={'priority': active_priority})
        response = self.client.get(edit_address_url)
        self.assertEqual(response.status_code, 200)
        payload = {'shipping_address': json.loads(response.content.decode('utf-8')).get('shipping_address_form')}
        payload['shipping_address'].update(plugin_order='1', active_priority=active_priority)
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        self.assertTrue('shipping_address_form' in response)
        self.assertEqual(response['shipping_address_form'].pop('active_priority'), '1')
        self.assertEqual(response['shipping_address_form'].pop('plugin_order'), '1')
        siblings_summary = response['shipping_address_form'].pop('siblings_summary')
        self.assertEqual(len(siblings_summary), 2)
        self.assertEqual(response['shipping_address_form'].pop('address2'), empty_field)
        self.assertDictEqual(response['shipping_address_form'], first_address)

        # check that Charles selected the first address
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.shipping_address.as_text(),
                         "Charles Smith\n507, Dudley St.\nPA 19148 Philadelphia\nUnited States\n")

        # now Charles removes his first address
        response = self.client.delete(edit_address_url)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content.decode('utf-8'))
        siblings_summary = response['shipping_address_form'].pop('siblings_summary')
        self.assertListEqual(siblings_summary, [
            {"value":"2","label":"1. Charles Smith – 1012, Madison Ave – MD 21201 Baltimore – United States"}
        ])
        self.assertEqual(response['shipping_address_form'].pop('active_priority'), '2')
        self.assertFalse(response['shipping_address_form'].pop('use_primary_address'))
        self.assertEqual(response['shipping_address_form'].pop('address2'), empty_field)
        self.assertDictEqual(response['shipping_address_form'], second_address)

        # check that Charles selected the second address
        self.cart.refresh_from_db()
        self.assertEqual(str(self.cart.shipping_address.priority), '2')
        self.assertEqual(ShippingAddress.objects.filter(customer=self.customer).count(), 1)
