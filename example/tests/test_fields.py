# -*- coding: utf-8
from __future__ import unicode_literals

import pytest

import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from shop.models.fields import JSONField

from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.customer import Customer
from shop.models.defaults.commodity import Commodity

from .models import TestChoices, ChoiceEnumFieldTestModel


class JsonModel(models.Model):

    class Meta:
        app_label = 'JsonModel'

    json = JSONField()
    default_json = JSONField(default=lambda: {"check": 12})


class JSONFieldTest(TestCase):
    """JSONField Tests"""

    @pytest.mark.django_db
    def setUp(self):
        super(JSONFieldTest, self).setUp()
        user = get_user_model().objects.create()
        customer = Customer.objects.create(number=1, user=user)
        product = Commodity.objects.create(
            product_code="testproduct",
            unit_price=decimal.Decimal("0"),
            order=1,
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


def test_choice_enum():
    assert TestChoices.default() is TestChoices.OPT_A
    assert TestChoices.OPT_A.name == 'OPT_A'
    assert TestChoices.OPT_A.value == 0

    choices = TestChoices.choices()
    assert choices[1][0] == 1
    assert choices[1][1].__str__() == 'TestChoices.OPT_B'


@pytest.mark.django_db
def test_choice_enum_field():
    obj = ChoiceEnumFieldTestModel.objects.create()
    assert obj.pk is not None
    assert obj.f is TestChoices.OPT_A
    obj.f = TestChoices.OPT_B
    obj.save()
