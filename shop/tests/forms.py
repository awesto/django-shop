# -*- coding: utf-8 -*-
"""Tests for the forms of the django-shop app."""
from django.contrib.auth.models import User
from django.test import TestCase

from shop.forms import CartItemModelForm, get_cart_item_formset
from shop.models.cartmodel import Cart, CartItem
from shop.models.productmodel import Product


class BaseCartItemFormsTestCase(TestCase):
    """Base class for tests related to ``CartItem`` forms and formsets."""

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Tester")
        self.cart = Cart.objects.create()
        self.product = Product.objects.create(unit_price=123)
        self.item = CartItem.objects.create(cart=self.cart, quantity=2,
                                            product=self.product)


class CartItemModelFormTestCase(BaseCartItemFormsTestCase):
    """Tests for the ``CartItemModelForm`` form class."""

    def test_setting_quantity_to_0_removes_cart_item(self):
        data = {
            'quantity': '0',
        }
        form = CartItemModelForm(instance=self.item, data=data)
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
        self.cart.update()
        items = self.cart.get_updated_cart_items()
        formset = get_cart_item_formset(cart_items=items)
        self.assertEqual(formset.forms[0].instance.line_subtotal, 246)
