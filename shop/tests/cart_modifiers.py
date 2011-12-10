#-*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test.testcases import TestCase
from shop.cart import modifiers_pool
from shop.cart.cart_modifiers_base import BaseCartModifier
from shop.cart.modifiers.tax_modifiers import TenPercentPerItemTaxModifier
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.cartmodel import Cart
from shop.models.productmodel import Product
from shop.tests.utils.context_managers import SettingsOverride


class CarModifierUsingStatePassing(BaseCartModifier):
    """
    A test cart modifier that uses the state variable to pass things around
    """
    def process_cart_item(self, cart_item, state):
        state['TEST'] = 'VALID'
        return cart_item

    def process_cart(self, cart, state):
        result = state['TEST']
        assert result == 'VALID'
        return cart


class CartModifiersTestCase(TestCase):

    PRODUCT_PRICE = Decimal('100')

    def setUp(self):
        cart_modifiers_pool.USE_CACHE = False
        self.user = User.objects.create(username="test",
            email="test@example.com")
        self.product = Product()
        self.product.name = "TestPrduct"
        self.product.slug = "TestPrduct"
        self.product.short_description = "TestPrduct"
        self.product.long_description = "TestPrduct"
        self.product.active = True
        self.product.unit_price = self.PRODUCT_PRICE
        self.product.save()

        self.cart = Cart()
        self.cart.user = self.user
        self.cart.save()

    def test_01_cart_modifier_pool_loads_modifiers_properly(self):
        """
        Let's add a price modifier to the settings, then load it,
        then call a method on it to make sure it works.
        """
        MODIFIERS = [
            'shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            thelist = modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            self.assertEqual(len(thelist), 1)
            instance = thelist[0]
            self.assertTrue(hasattr(instance, 'TAX_PERCENTAGE'))

    def test_02_cart_modifiers_pool_handles_wrong_path(self):
        MODIFIERS = ['shop2.cart.modifiers.tax_modifiers']  # wrong path
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            raised = False
            try:
                modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            except:
                raised = True
            self.assertTrue(raised)

    def test_03_cart_modifiers_pool_handles_wrong_module(self):
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.IdontExist']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            raised = False
            try:
                modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            except ImproperlyConfigured:
                raised = True
            self.assertTrue(raised)

    def test_03_cart_modifiers_pool_handles_not_a_path(self):
        MODIFIERS = ['shop']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            raised = False
            try:
                modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            except ImproperlyConfigured:
                raised = True
            self.assertTrue(raised)

    def test_state_is_passed_around_properly(self):
        MODIFIERS = ['shop.tests.cart_modifiers.CarModifierUsingStatePassing']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            self.cart.add_product(self.product)
            self.cart.save()
            self.cart.update()  # This should raise if the state isn't passed


class TenPercentPerItemTaxModifierTestCase(TestCase):

    class MockItem(object):
        """ A simple mock object to assert the tax modifier works properly"""
        def __init__(self):
            self.line_subtotal = 100  # Makes testing easy
            self.current_total = self.line_subtotal
            self.extra_price_fields = []

    def test_tax_amount_is_correct(self):
        modifier = TenPercentPerItemTaxModifier()
        item = self.MockItem()
        field = modifier.get_extra_cart_item_price_field(item)
        self.assertTrue(field[1] == Decimal('10'))

    def test_tax_amount_is_correct_after_modifier(self):
        modifier = TenPercentPerItemTaxModifier()
        item = self.MockItem()
        previous_option = ('Some option', 10)
        item.extra_price_fields.append(previous_option)
        item.current_total = item.current_total + previous_option[1]
        field = modifier.get_extra_cart_item_price_field(item)
        self.assertTrue(field[1] == Decimal('11'))
