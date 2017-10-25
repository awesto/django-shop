# -*- coding: utf-8
from __future__ import unicode_literals

import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from shop.models.fields import JSONField, ChoiceEnum, ChoiceEnumField

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


class MyChoices(ChoiceEnum):
    A = 0
    B = 1


class EnumTest(TestCase):
    def test_enum(self):
        choice_a = MyChoices.A
        self.assertIsInstance(choice_a, MyChoices)
        self.assertEqual(MyChoices.B.name, 'B')
        self.assertEqual(MyChoices.B.value, 1)
        choice_b = MyChoices('B')
        self.assertEqual(str(choice_b), 'MyChoices.B')
        self.assertEqual(MyChoices.default(), MyChoices.A)
        self.assertListEqual(MyChoices.choices(), [(0, 'MyChoices.A'), (1, 'MyChoices.B')])


class EnumFieldTests(TestCase):
    def test_to_python(self):
        f = ChoiceEnumField(enum_type=MyChoices)
        self.assertEqual(f.to_python(0), MyChoices.A)
        self.assertEqual(f.to_python('A'), MyChoices.A)
        self.assertEqual(f.to_python(1), MyChoices.B)
        with self.assertRaises(ValueError):
            f.to_python(None)
        with self.assertRaises(ValueError):
            f.to_python(3)

    def test_deconstruct(self):
        f = ChoiceEnumField(enum_type=MyChoices)
        name, path, args_, kwargs_ = f.deconstruct()
        self.assertIsNone(name)
        self.assertEqual(path, 'shop.models.fields.ChoiceEnumField')
        self.assertListEqual(args_, [])
        self.assertDictEqual(kwargs_, {})

    def test_from_db_value(self):
        f = ChoiceEnumField(enum_type=MyChoices)
        self.assertEqual(f.from_db_value(0, None, None, None), MyChoices.A)
        self.assertEqual(f.from_db_value(1, None, None, None), MyChoices.B)
        self.assertEqual(f.from_db_value(2, None, None, None), 2)

    def test_get_prep_value(self):
        f = ChoiceEnumField(enum_type=MyChoices)
        self.assertEqual(f.get_prep_value(MyChoices.A), 0)
        self.assertEqual(f.get_prep_value(MyChoices.B), 1)
        with self.assertRaises(ValueError):
            f.get_prep_value('X')

    def test_value_to_string(self):
        f = ChoiceEnumField(enum_type=MyChoices)
        self.assertEqual(f.value_to_string(MyChoices.A), 'A')
        self.assertEqual(f.value_to_string(MyChoices.B), 'B')
        with self.assertRaises(ValueError):
            f.value_to_string(0)
