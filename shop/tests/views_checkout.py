#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from shop.clientmodel.models import Country, Address
from shop.tests.util import Mock
from shop.views.checkout import CheckoutSelectionView
        
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
        setattr(self.request, 'method', 'GET')
    
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
        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)
    
    def test_shipping_address_form_user_no_preset(self):
        setattr(self.request, 'user', self.user)
        
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
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)
    
    def test_billing_address_form_user_no_preset(self):
        setattr(self.request, 'user', self.user)
        
        address = Address.objects.create(country=self.country, user_billing=self.user)
        address.save()
        
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertEqual(res.instance, address)

    #===========================================================================
    # Billing and shipping form
    #===========================================================================

    def test_billing_and_shipping_selection_post(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_and_shipping_selection_form()
        self.assertNotEqual(res, None)
        
    def test_billing_and_shipping_selection_get(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_and_shipping_selection_form()
        self.assertNotEqual(res, None)
        
    def test_billing_and_shipping_selection_cached(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_and_shipping_selection_form()
        res2 = view.get_billing_and_shipping_selection_form()
        self.assertEqual(res, res2)

    #===========================================================================
    # Context Data
    #===========================================================================
    
    def test_get_context_data(self):
        setattr(self.request, 'method', 'GET')
        view = CheckoutSelectionView(request=self.request)
        ctx = view.get_context_data()
        self.assertNotEqual(ctx, None)
        self.assertNotEqual(ctx['shipping_address'], None)
        self.assertNotEqual(ctx['billing_address'], None)
        self.assertNotEqual(ctx['billing_shipping_form'], None)
        
