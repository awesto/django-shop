# -*- coding: utf-8
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import get_user_model
from shop.models.defaults.address import ShippingAddress, BillingAddress  # noqa
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
        shipping_addr = ShippingAddress.objects.create(priority=1, customer=self.customer)
        self.assertGreaterEqual(shipping_addr.id, 1)
        billing_addr = BillingAddress.objects.create(priority=1, customer=self.customer)
        self.assertGreaterEqual(shipping_addr.id, 1)
