# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.test import TestCase

from shop.models.defaults.cart_item import CartItem
from shop.models.fields import JSONField


class JsonModel(models.Model):

    class Meta:
        app_label = 'JsonModel'

    json = JSONField()
    default_json = JSONField(default={"check": 12})


class JSONFieldTest(TestCase):
    """JSONField Tests"""
    def setUp(self):
        super(JSONFieldTest, self).setUp()
        self.sample = CartItem.objects.get(id=8)
        self.assertIsNotNone(self.sample)

    def XXX_json_field_create(self):
        """Test saving a JSON object in our JSONField"""
        extra = {"product_code":"1121"}

        self.assertEqual(self.sample.extra, extra)
