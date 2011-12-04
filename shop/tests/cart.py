# -*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.cartmodel import Cart, CartItem
from shop.models.productmodel import Product
from shop.tests.utils.context_managers import SettingsOverride

# This try except is there to let people run the tests from any project
# Not only from the provided "test" project.
SKIP_BASEPRODUCT_TEST = False
try:
    from project.models import BaseProduct
except:
    SKIP_BASEPRODUCT_TEST = True


class CartTestCase(TestCase):
    PRODUCT_PRICE = Decimal('100')
    TEN_PERCENT = Decimal(10) / Decimal(100)

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

    def test_empty_cart_costs_0_quantity_0(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):

            self.cart.update()

            self.assertEqual(self.cart.subtotal_price, Decimal('0.0'))
            self.assertEqual(self.cart.total_price, Decimal('0.0'))
            self.assertEqual(self.cart.total_quantity, 0)

    def test_one_object_no_modifiers(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.cart.add_product(self.product)
            self.cart.save()
            self.cart.update()
            self.cart.save()

            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_quantity, 1)

    def test_two_objects_no_modifier(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):

            # We add two objects now :)
            self.cart.add_product(self.product, 2)
            self.cart.update()
            self.cart.save()

            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE * 2)
            self.assertEqual(self.cart.total_price, self.PRODUCT_PRICE * 2)
            self.assertEqual(self.cart.total_quantity, 2)

    def test_one_object_simple_modifier(self):
        MODIFIERS = [
            'shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            self.cart.add_product(self.product)
            self.cart.update()
            self.cart.save()

            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_price,
                (self.TEN_PERCENT * self.PRODUCT_PRICE) + self.PRODUCT_PRICE)

    def test_one_object_two_modifiers_no_rebate(self):
        MODIFIERS = [
            'shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier',
            'shop.cart.modifiers.rebate_modifiers.BulkRebateModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            self.cart.add_product(self.product)

            self.cart.update()
            self.cart.save()

            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_price,
                (self.TEN_PERCENT * self.PRODUCT_PRICE) + self.PRODUCT_PRICE)

    def test_one_object_two_modifiers_with_rebate(self):
        MODIFIERS = [
            'shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier',
            'shop.cart.modifiers.rebate_modifiers.BulkRebateModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            # We add 6 objects now :)
            self.cart.add_product(self.product, 6)
            self.cart.update()
            self.cart.save()

            #subtotal is 600 - 10% = 540
            sub_should_be = (6 * self.PRODUCT_PRICE) - (
                self.TEN_PERCENT * (6 * self.PRODUCT_PRICE))

            total_should_be = sub_should_be + (
                self.TEN_PERCENT * sub_should_be)

            self.assertEqual(self.cart.subtotal_price, sub_should_be)
            self.assertEqual(self.cart.total_price, total_should_be)

    def test_add_same_object_twice(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.assertEqual(self.cart.total_quantity, 0)
            self.cart.add_product(self.product)
            self.cart.add_product(self.product)
            self.cart.update()
            self.cart.save()

            self.assertEqual(len(self.cart.items.all()), 1)
            self.assertEqual(self.cart.items.all()[0].quantity, 2)
            self.assertEqual(self.cart.total_quantity, 2)

    def test_add_same_object_twice_no_merge(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.assertEqual(self.cart.total_quantity, 0)
            self.cart.add_product(self.product, merge=False)
            self.cart.add_product(self.product, merge=False)
            self.cart.update()
            self.cart.save()

            self.assertEqual(len(self.cart.items.all()), 2)
            self.assertEqual(self.cart.items.all()[0].quantity, 1)
            self.assertEqual(self.cart.items.all()[1].quantity, 1)

    def test_add_product_updates_last_updated(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            initial = self.cart.last_updated
            self.cart.add_product(self.product)
            self.assertNotEqual(initial, self.cart.last_updated)

    def test_cart_item_should_use_specific_type_to_get_price(self):
        if SKIP_BASEPRODUCT_TEST:
            return
        base_product = BaseProduct.objects.create(
            unit_price=self.PRODUCT_PRICE)
        variation = base_product.productvariation_set.create(
            name="Variation 1")
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.cart.add_product(variation)
            self.cart.update()
            self.cart.save()
            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)

    def test_update_quantity_deletes(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.assertEqual(self.cart.total_quantity, 0)
            self.cart.add_product(self.product)
            self.cart.add_product(self.product)
            self.cart.update()
            self.cart.save()

            self.assertEqual(len(self.cart.items.all()), 1)
            self.cart.update_quantity(self.cart.items.all()[0].id, 0)
            self.assertEqual(len(self.cart.items.all()), 0)

    def test_custom_queryset_is_used_when_passed_to_method(self):
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            # first we add any product
            self.cart.add_product(self.product)

            # now we try to select a CartItem that does not exist yet. This
            # could be an item with a yet unused combination of variations.
            qs = CartItem.objects.filter(cart=self.cart, product=self.product,
                                         quantity=42)
            # although we add the same product and have merge=True, there
            # should be a new CartItem being created now.
            self.cart.add_product(self.product, queryset=qs)
            self.assertEqual(len(self.cart.items.all()), 2)

    def test_get_updated_cart_items(self):
        self.cart.add_product(self.product)
        self.cart.update()
        cached_cart_items = self.cart.get_updated_cart_items()

        cart_items = CartItem.objects.filter(cart=self.cart)
        for item in cart_items:
            item.update({})

        self.assertEqual(len(cached_cart_items), len(cart_items))
        self.assertEqual(cached_cart_items[0].line_total,
                cart_items[0].line_total)

    def test_get_updated_cart_items_without_updating_cart(self):
        with self.assertRaises(AssertionError):
            self.cart.get_updated_cart_items()
