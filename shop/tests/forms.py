# -*- coding: utf-8 -*-
"""Tests for the forms of the django-shop app."""
from django.contrib.auth.models import User
from django import forms
from django.test import TestCase
from django.test.utils import override_settings

from shop.forms import (CartItemModelForm, get_cart_item_modelform_class,
                        get_cart_item_formset)
from shop.tests.util import Mock
from shop.models.cartmodel import Cart, CartItem
from shop.models.productmodel import Product


class CartItemModelForm(CartItemModelForm):
    quantity = forms.IntegerField(min_value=5, max_value=9999)


class BaseCartItemFormsTestCase(TestCase):
    """Base class for tests related to ``CartItem`` forms and formsets."""

    def setUp(self):
        user = User.objects.create(username="test", email="test@example.com",
                                   first_name="Test", last_name="Tester")
        self.request = Mock()
        setattr(self.request, 'user', user)
        self.cart = Cart.objects.create()
        self.product = Product.objects.create(unit_price=123)
        self.item = CartItem.objects.create(cart=self.cart, quantity=2,
                                            product=self.product)


class CartItemModelFormTestCase(BaseCartItemFormsTestCase):
    """Tests for the ``CartItemModelForm`` form class."""

    @override_settings(SHOP_CART_ITEM_FORM="shop.tests.forms.CartItemModelForm")
    def test_custom_cartitem_modelform(self):
        data = {
            'quantity': '0',
        }
        form = get_cart_item_modelform_class()(instance=self.item, data=data)
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(str(form.errors).find("quantity") > -1)
        self.assertTrue(str(form.errors).find("greater than or equal to 5") > -1)

        data = {
            'quantity': '6',
        }
        form = get_cart_item_modelform_class()(instance=self.item, data=data)
        self.assertEqual(len(form.errors), 0)
        form.save()
        self.assertEqual(1, CartItem.objects.all().count())

    def test_setting_quantity_to_0_removes_cart_item(self):
        data = {
            'quantity': '0',
        }
        form = get_cart_item_modelform_class()(instance=self.item, data=data)
        self.assertEqual(len(form.errors), 0)
        form.save()
        self.assertEqual(0, CartItem.objects.all().count())


class GetCartItemFormsetTestCase(BaseCartItemFormsTestCase):
    """Tests for the ``get_cart_item_formset()`` method."""

    def test_should_return_formset(self):
        items = CartItem.objects.all()
        formset = get_cart_item_formset(cart_items=items)
        self.assertTrue('quantity' in formset.forms[0].fields)

    def test_cart_items_should_have_updated_values(self):
        self.cart.update(self.request)
        items = self.cart.get_updated_cart_items()
        formset = get_cart_item_formset(cart_items=items)
        self.assertEqual(formset.forms[0].instance.line_subtotal, 246)
