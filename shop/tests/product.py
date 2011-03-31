# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.models.productmodel import Product
from django.test.testcases import TestCase

class ProductTestCase(TestCase):

    def create_fixtures(self):
        
        self.product = Product()
        self.product.name = 'test'
        self.product.short_description = 'test'
        self.product.long_description = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
    
    def test_01_unicode_returns_proper_stuff(self):
        self.create_fixtures()
        ret = self.product.__unicode__()
        self.assertEqual(ret, self.product.name)
        
    def test_02_specify_returns_self_when_not_a_subclass(self):
        self.create_fixtures()
        ret = self.product.get_specific()
        self.assertEqual(ret, self.product)
        
    def test_03_active_filter_returns_only_active_products(self):
        self.create_fixtures()
        ret1 = len(Product.objects.active())
        # Set self.product to be active
        self.product.active = True
        self.product.save()
        ret2 = len(Product.objects.active())
        self.assertNotEqual(ret1, ret2)
        self.assertEqual(ret1, 0)
        self.assertEqual(ret2, 1)
    