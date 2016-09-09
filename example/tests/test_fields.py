# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.test import TestCase

from shop.models.fields import JSONField


class JsonModel(models.Model):
    json = JSONField()
    default_json = JSONField(default={"check": 12})


class JSONFieldTest(TestCase):
    """JSONField Wrapper Tests"""

    def test_json_field_create(self):
        """Test saving a JSON object in our JSONField"""
        json_obj = {
            "item_1": "this is a json blah",
            "blergh": "hey, hey, hey"}

        obj = JsonModel.objects.create(json=json_obj)
        new_obj = JsonModel.objects.get(id=obj.id)

        self.assertEqual(new_obj.json, json_obj)
