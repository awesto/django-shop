# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.models.productmodel import Product
from django.test.testcases import TestCase

class ProductTestCase(TestCase):

    def create_fixtures(self):
        
        self.product = Product()
        self.product.name = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
    
    def test_unicode_returns_proper_stuff(self):
        self.create_fixtures()
        ret = self.product.__unicode__()
        self.assertEqual(ret, self.product.name)
        
    def test_active_filter_returns_only_active_products(self):
        self.create_fixtures()
        ret1 = len(Product.objects.active())
        # Set self.product to be active
        self.product.active = True
        self.product.save()
        ret2 = len(Product.objects.active())
        self.assertNotEqual(ret1, ret2)
        self.assertEqual(ret1, 0)
        self.assertEqual(ret2, 1)
    
