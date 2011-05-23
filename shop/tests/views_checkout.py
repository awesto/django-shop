#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from shop.clientmodel.models import Country, Address
from shop.tests.util import Mock
from shop.views.checkout import CheckoutSelectionView

#class CheckoutViewTestCase(TestCase):
#    def setUp(self): 
#        self.user = User.objects.create(username="test", 
#                                        email="test@example.com",
#                                        first_name="Test",
#                                        last_name = "Tester")
#        
#        self.cart = Cart.objects.create()
#        self.product= Product.objects.create()
#        self.item = CartItem.objects.create(cart=self.cart, quantity=1, 
#                                            product=self.product)
#
#    def test_select_shipping_view(self):
#        request = Mock()
#        setattr(request, 'is_ajax', lambda : False)
#        setattr(request, 'user', self.user)
#        post={
#            'add_item_id':self.product.id,
#            'add_item_quantity':1,
#        }
#
#        view = SelectShippingView(request=request)
#        view.create_order_object_from_cart()
#        #TODO: Check more exensively that the order created is correct
        
class ShippingBillingViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        
        self.country = Country.objects.create(name="Switzerland")
        
        self.address = Address.objects.create(country=self.country)
        
        self.request = Mock()
        setattr(self.request, 'user', None)
        setattr(self.request, 'session', {})
    
    def test_shipping_address_cache(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)
        res2 = view.get_shipping_address_form()
        self.assertEqual(res, res2)
    
    def test_shipping_address_form_post(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)
    
    def test_shipping_address_form_user_preset(self):
        setattr(self.request, 'method', 'GET')
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)
    
    def test_shipping_address_form_user_no_preset(self):
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'method', 'GET')
        
        address = Address.objects.create(country=self.country, user_shipping=self.user)
        address.save()
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertEqual(res.instance, address)
    
    def test_billing_address_cache(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)
        res2 = view.get_billing_address_form()
        self.assertEqual(res, res2)
    
    def test_billing_address_form_post(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)
    
    def test_billing_address_form_user_preset(self):
        setattr(self.request, 'method', 'GET')
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)
    
    def test_billing_address_form_user_no_preset(self):
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'method', 'GET')
        
        address = Address.objects.create(country=self.country, user_billing=self.user)
        address.save()
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertEqual(res.instance, address)
