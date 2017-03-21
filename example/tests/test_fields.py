# -*- coding: utf-8
from __future__ import unicode_literals

import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from shop.models.fields import JSONField

from myshop.models import Cart, CartItem, Customer
from myshop.models.manufacturer import Manufacturer
from myshop.models import Commodity


class JsonModel(models.Model):

    class Meta:
        app_label = 'JsonModel'

    json = JSONField()
    default_json = JSONField(default=lambda: {"check": 12})


class JSONFieldTest(TestCase):
    """JSONField Tests"""

    def setUp(self):
        super(JSONFieldTest, self).setUp()
        user = get_user_model().objects.create()
        customer = Customer.objects.create(number=1, user=user)
        manufacturer = Manufacturer.objects.create()
        product = Commodity.objects.create(
            product_code="testproduct",
            unit_price=decimal.Decimal("0"),
            order=1,
            manufacturer=manufacturer
        )
        cart = Cart.objects.create(customer=customer)
        self.sample = CartItem.objects.create(
            quantity=1,
            cart=cart,
            product=product,
            extra={'product_code': 'foo'},
        )
        self.assertIsNotNone(self.sample)

    def test_json_field_create(self):
        """Test saving a JSON object in our JSONField"""
        extra = {'product_code': 'foo'}
        self.assertEqual(self.sample.extra, extra)
