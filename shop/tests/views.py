#-*- coding: utf-8 -*-
from decimal import Decimal
from shop.models.productmodel import Product, Category
from shop.views.category import CategoryDetailView
from shop.views.product import ProductDetailView
from unittest import TestCase
from shop.views.cart import CartDetails



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
        setattr(self.view, 'object', None)
        obj = self.view.get_object()
        inst = isinstance(obj,Product)
        self.assertEqual(inst, True)
        
    # This is commented out until the following gets solved:
    # http://code.djangoproject.com/ticket/15329
    def test_02_get_templates_return_expected_values(self):
        self.view = ProductDetailView()
        setattr(self.view, 'object', None)
        tmp = self.view.get_template_names()
        self.assertEqual(len(tmp), 1)

class CategoryDetailViewTestCase(TestCase):
    def setUp(self):
        self.cat = Category()
        self.cat.name = 'Test Category'
        self.cat.save()
        
        self.product = Product()
        self.product.category = self.cat
        self.product.name = 'test'
        self.product.short_description = 'test'
        self.product.long_description = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
    
    def tearDown(self):
        self.cat.delete()
        self.product.delete()
    
    def test_01_get_context_works(self):
        view = CategoryDetailView(kwargs={'pk':self.cat.id})
        setattr(view, 'object', view.get_object())
        ret = view.get_context_data()
        self.assertEqual(len(ret), 1)
        
    def test_02_get_context_works_with_list_of_products(self):
        self.product.active = True
        self.product.save()
        view = CategoryDetailView(kwargs={'pk':self.cat.id})
        setattr(view, 'object', view.get_object())
        ret = view.get_context_data()
        self.assertEqual(len(ret), 2)
