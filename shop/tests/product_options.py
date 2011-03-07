#-*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.cartmodel import Cart, CartItem
from shop.models.productmodel import Product
from shop.tests.utils.context_managers import SettingsOverride

class ProductOptionsTestCase(TestCase):
    
    PRODUCT_PRICE = Decimal('100')
    TEN_PERCENT = Decimal(10) / Decimal(100)
    
    def create_fixtures(self):
        cart_modifiers_pool.USE_CACHE=False
        
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        
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
        
    
    def test_01_no_options_yield_normal_price(self):
        self.assertEqual(Cart.objects.count(), 0)
        self.assertEqual(CartItem.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)
        self.create_fixtures()
        MODIFIERS = ['shop.cart.modifiers.product_options.ProductOptionsModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            self.cart.add_product(self.product,1)
            self.cart.update()
            self.cart.save()
            sub_should_be = 1*self.PRODUCT_PRICE 
            total_should_be = sub_should_be 
            
            self.assertEqual(self.cart.subtotal_price, sub_should_be)
            self.assertEqual(self.cart.total_price, total_should_be)
            