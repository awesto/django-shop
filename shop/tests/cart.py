# -*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.cartmodel import Cart
from shop.models.productmodel import Product
from shop.tests.utils.context_managers import SettingsOverride
from project.models import BaseProduct


class CartTestCase(TestCase):
    PRODUCT_PRICE = Decimal('100')
    TEN_PERCENT = Decimal(10) / Decimal(100)
    
    def create_fixtures(self):
        
        cart_modifiers_pool.USE_CACHE=False
        
        self.user = User.objects.create(username="test", email="test@example.com")
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
    
    def test_01_empty_cart_costs_0(self):
        self.create_fixtures()
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            
            self.cart.update()
            
            self.assertEqual(self.cart.subtotal_price, Decimal('0.0'))
            self.assertEqual(self.cart.total_price, Decimal('0.0'))
            
    def test_02_one_object_no_modifiers(self):
        self.create_fixtures()
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.cart.add_product(self.product)
            self.cart.save()
            self.cart.update()
            self.cart.save()
            
            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_price, self.PRODUCT_PRICE)
    
    def test_03_two_objects_no_modifier(self):
        self.create_fixtures()
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            
            # We add two objects now :)
            self.cart.add_product(self.product,2)
            self.cart.update()
            self.cart.save()
            
            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE*2)
            self.assertEqual(self.cart.total_price, self.PRODUCT_PRICE*2)
            
    def test_04_one_object_simple_modifier(self):
        self.create_fixtures()
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            self.cart.add_product(self.product)
            self.cart.update()
            self.cart.save()
            
            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_price, (self.TEN_PERCENT*self.PRODUCT_PRICE)+self.PRODUCT_PRICE)
            
    def test_05_one_object_two_modifiers_no_rebate(self):
        self.create_fixtures()
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier',
                     'shop.cart.modifiers.rebate_modifiers.BulkRebateModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            self.cart.add_product(self.product)
            
            self.cart.update()
            self.cart.save()
            
            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
            self.assertEqual(self.cart.total_price, (self.TEN_PERCENT*self.PRODUCT_PRICE)+self.PRODUCT_PRICE)
            
    def test_06_one_object_two_modifiers_with_rebate(self):
        self.create_fixtures()
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier',
                     'shop.cart.modifiers.rebate_modifiers.BulkRebateModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            # We add 6 objects now :)
            self.cart.add_product(self.product,6)
            self.cart.update()
            self.cart.save()
            
            #subtotal is 600 - 10% = 540
            sub_should_be = (6*self.PRODUCT_PRICE) - (self.TEN_PERCENT*(6*self.PRODUCT_PRICE)) 
            
            total_should_be = sub_should_be + (self.TEN_PERCENT*sub_should_be) 
            
            self.assertEqual(self.cart.subtotal_price, sub_should_be)
            self.assertEqual(self.cart.total_price, total_should_be)
            
    def test_07_add_same_object_twice(self):
        self.create_fixtures()
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.cart.add_product(self.product)
            self.cart.add_product(self.product)
            self.cart.update()
            self.cart.save()
            
            self.assertEqual(len(self.cart.items.all()),1)
            self.assertEqual(self.cart.items.all()[0].quantity, 2)
            
    def test_08_add_product_updates_last_updated(self):
        self.create_fixtures()
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            initial = self.cart.last_updated
            self.cart.add_product(self.product)
            self.assertNotEqual(initial, self.cart.last_updated)

    def test_09_cart_item_should_use_specific_type_to_get_price(self):
        self.create_fixtures()
        base_product = BaseProduct.objects.create(unit_price=self.PRODUCT_PRICE)
        variation = base_product.productvariation_set.create(
                name="Variation 1"
                )
        with SettingsOverride(SHOP_CART_MODIFIERS=[]):
            self.cart.add_product(variation)
            self.cart.update()
            self.cart.save()
            self.assertEqual(self.cart.subtotal_price, self.PRODUCT_PRICE)
