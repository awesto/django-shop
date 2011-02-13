# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.models.productmodel import Product
from unittest import TestCase

class ProductTestCase(TestCase):

    def setUp(self):
        self.product = Product()
        self.product.name = 'test'
        self.product.short_description = 'test'
        self.product.long_description = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
    
    def tearDown(self):
        self.product.delete()
    
    def test_01_unicode_returns_proper_stuff(self):
        ret = self.product.__unicode__()
        self.assertEqual(ret, self.product.name)
        
    def test_02_specify_returns_self_when_not_a_subclass(self):
        ret = self.product.specify()
        self.assertEqual(ret, self.product)
        
    def test_03_active_filter_returns_only_active_products(self):
        ret1 = len(Product.objects.active())
        # Set self.product to be active
        self.product.active = True
        self.product.save()
        ret2 = len(Product.objects.active())
        self.assertNotEqual(ret1, ret2)
        self.assertEqual(ret1, 0)
        self.assertEqual(ret2, 1)
        