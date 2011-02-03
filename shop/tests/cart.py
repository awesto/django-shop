# -*- coding: utf-8 -*-
from __future__ import with_statement
from django.contrib.auth.models import User
from shop.models.cartmodel import Cart
from shop.models.productmodel import Product
from shop.tests.utils.context_managers import SettingsOverride
from unittest import TestCase

class CartTestCase(TestCase):
    
    def test_01_empty_cart_costs_0(self):
        with SettingsOverride(SHOP_PRICE_MODIFIERS=[]):
            user = User.objects.create(username="test", email="test@example.com")
            
            product = Product()
            
            product.name = "TestPrduct"
            product.slug = "TestPrduct"
            product.short_description = "TestPrduct"
            product.long_description = "TestPrduct"
            product.active = True
            product.base_price = '12.0'
            
            product.save()
            
            cart = Cart()
            cart.user = user
            cart.save()
            
            cart.update()
            
            self.assertEqual(cart.subtotal_price, 0.0)
            self.assertEqual(cart.total_price, 0.0)
            
    def test_02_one_object_no_modifiers(self):
        pass
    
    def test_03_one_object_one_modifier(self):
        pass