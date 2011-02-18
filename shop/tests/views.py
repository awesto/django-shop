#-*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.test.testcases import TestCase
from shop.models.cartmodel import Cart, CartItem
from shop.models.productmodel import Product, Category
from shop.tests.util import Mock
from shop.views.cart import CartDetails
from shop.views.category import CategoryDetailView
from shop.views.product import ProductDetailView

class ProductDetailViewTestCase(TestCase):
    def create_fixtures(self):
        
        self.product = Product()
        self.product.name = 'test'
        self.product.short_description = 'test'
        self.product.long_description = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
        
        self.view = ProductDetailView(kwargs={'pk':self.product.id})
    
    def test_01_get_product_returns_correctly(self):
        self.create_fixtures()
        setattr(self.view, 'object', None)
        obj = self.view.get_object()
        inst = isinstance(obj,Product)
        self.assertEqual(inst, True)
        
    def test_02_get_templates_return_expected_values(self):
        self.create_fixtures()
        self.view = ProductDetailView()
        setattr(self.view, 'object', None)
        tmp = self.view.get_template_names()
        self.assertEqual(len(tmp), 1)

class CategoryDetailViewTestCase(TestCase):
    def create_fixtures(self):
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
    
    def test_01_get_context_works(self):
        self.create_fixtures()
        view = CategoryDetailView(kwargs={'pk':self.cat.id})
        setattr(view, 'object', view.get_object())
        ret = view.get_context_data()
        self.assertEqual(len(ret), 1)
        
    def test_02_get_context_works_with_list_of_products(self):
        self.create_fixtures()
        self.product.active = True
        self.product.save()
        view = CategoryDetailView(kwargs={'pk':self.cat.id})
        setattr(view, 'object', view.get_object())
        ret = view.get_context_data()
        self.assertEqual(len(ret), 2)
        
class CartDetailsViewTestCase(TestCase):
    def create_fixtures(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Tester")
        
        self.cart = Cart.objects.create()
        self.product= Product.objects.create()
        self.item = CartItem.objects.create(cart=self.cart, quantity=1, 
                                            product=self.product)
        
        
    def test_01_get_context_data_works(self):
        self.create_fixtures()
        request = Mock()
        setattr(request, 'user', self.user)
        view = CartDetails(request=request)
        ret = view.get_context_data()
        self.assertNotEqual(ret,None)
        
    def test_02_context_has_as_many_items_as_cart(self):
        self.create_fixtures()
        self.cart.user = self.user
        self.cart.save()
        request = Mock()
        setattr(request, 'user', self.user)
        view = CartDetails(request=request)
        ret = view.get_context_data()
        self.assertNotEqual(ret,None)
        self.assertEqual(len(ret['cart_items']),1)
        self.assertEqual(ret['cart_items'][0], self.item)
        
    def test_03_calling_post_redirects_properly(self):
        self.create_fixtures()
        self.cart.user = self.user
        self.cart.save()
        
        request = Mock()
        setattr(request, 'is_ajax', lambda :False)
        setattr(request, 'user', self.user)
        post={
            'add_item_id':self.product.id,
            'add_item_quantity':1,
        }
        setattr(request, 'POST', post)
        
        view = CartDetails(request=request)
        ret = view.post()
        self.assertTrue(isinstance(ret,HttpResponseRedirect))
        
        ret = view.get_context_data()
        self.assertNotEqual(ret,None)
        self.assertEqual(len(ret['cart_items']),1)
        
        self.assertEqual(ret['cart_items'][0], self.item)
        self.assertEqual(ret['cart_items'][0].quantity, 2)
        
    def test_04_calling_ajax_post_returns_content(self):
        self.create_fixtures()
        self.cart.user = self.user
        self.cart.save()
        
        request = Mock()
        setattr(request, 'is_ajax', lambda :True)
        setattr(request, 'user', self.user)
        post={
            'add_item_id':self.product.id,
            'add_item_quantity':1,
        }
        setattr(request, 'POST', post)
        
        view = CartDetails(request=request)
        ret = view.post()
        self.assertTrue(isinstance(ret,HttpResponse))
        
        ret = view.get_context_data()
        self.assertNotEqual(ret,None)
        self.assertEqual(len(ret['cart_items']),1)
        
        self.assertEqual(ret['cart_items'][0], self.item)
        self.assertEqual(ret['cart_items'][0].quantity, 2)