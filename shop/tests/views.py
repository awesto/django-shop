#-*- coding: utf-8 -*-
from decimal import Decimal
from shop.models.productmodel import Product
from shop.views.product import ProductDetailView
from unittest import TestCase



class ProductDetailViewTestCase(TestCase):
    def setUp(self):
        
        self.product = Product()
        self.product.name = 'test'
        self.product.short_description = 'test'
        self.product.long_description = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
        
        self.view = ProductDetailView(kwargs={'pk':self.product.id})
    
    def tearDown(self):
        self.product.delete()
    
    def test_01_get_product_returns_correctly(self):
        obj = self.view.get_object()
        inst = isinstance(obj,Product)
        self.assertEqual(inst, True)
        
    # This is commented out until the following gets solved:
    # http://code.djangoproject.com/ticket/15329
#    def test_02_get_templates_return_expected_values(self):
#        self.view = ProductDetailView()
#        tmp = self.view.get_template_names()
#        import ipdb; ipdb.set_trace()
#        self.assertEqual(len(tmp), 1)
