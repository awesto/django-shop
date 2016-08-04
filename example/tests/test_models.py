# -*- coding: utf-8
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import get_user_model
from shop.models.defaults.address import ShippingAddress
from shop.models.defaults.customer import Customer


class AddressTest(TestCase):
    def setUp(self):
        super(AddressTest, self).setUp()
        User = get_user_model()
        user = {
            'username': 'john',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'secret',
        }
        user = User.objects.create(**user)
        self.customer = Customer.objects.create(user=user)
        self.assertGreaterEqual(self.customer.pk, 1)

    def test_shipping_address(self):
        address = {'name': "John Doe", 'address1': "31, Orwell Rd", 'zip_code': "L41RG",
            'city': "Liverpool", 'country': 'UK'}
        shipping_addr = ShippingAddress.objects.create(priority=1, customer=self.customer, **address)
        self.assertGreaterEqual(shipping_addr.id, 1)
        addr_block = "John Doe\n31, Orwell Rd\nL41RG Liverpool\nUK\n"
        self.assertMultiLineEqual(shipping_addr.as_text(), addr_block)
        self.assertEqual(ShippingAddress.objects.get_max_priority(self.customer), 1)
        self.assertEqual(ShippingAddress.objects.get_fallback(self.customer), shipping_addr)
