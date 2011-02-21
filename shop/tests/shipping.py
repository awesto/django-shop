#-*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from shop.backend_base import backends_pool
from shop.models.ordermodel import Order
from shop.tests.utils.context_managers import SettingsOverride
from django.test.testcases import TestCase

class MockShippingBackend(object):
    '''
    A simple, useless backend
    '''

class GeneralShippingBackendTestCase(TestCase):
    
    def create_fixtures(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        backends_pool.USE_CACHE = False
        
        self.order = Order()
        self.order.order_subtotal = Decimal('10')
        self.order.order_total = Decimal('10')
        self.order.amount_payed = Decimal('0')
        self.order.shipping_cost = Decimal('0')
        
        self.order.shipping_name = 'toto'
        self.order.shipping_address = 'address'
        self.order.shipping_address2 = 'address2'
        self.order.shipping_zip_code = 'zip'
        self.order.shipping_state = 'state'
        self.order.shipping_country = 'country'
        
        self.order.billing_name = 'toto'
        self.order.billing_address = 'address'
        self.order.billing_address2 = 'address2'
        self.order.billing_zip_code = 'zip'
        self.order.billing_state = 'state'
        self.order.billing_country = 'country'
        
        self.order.save()
    
#    def test_01_enforcing_of_name_works(self):
#        self.create_fixtures()
#        class MockBackend(BaseShippingBackend):
#            pass
#        
#        raised = False
#        
#        try:
#            MockBackend()
#        except NotImplementedError:
#            raised = True
#        
#        self.assertEqual(raised, True)
#        
#    def test_02_enforcing_of_namespace_works(self):
#        self.create_fixtures()
#        class MockBackend(BaseShippingBackend):
#            backend_name = "Fake"
#        
#        raised = False
#        
#        try:
#            MockBackend()
#        except NotImplementedError:
#            raised = True
#        
#        self.assertEqual(raised, True)
#        
#    def test_03_get_order_returns_sensible_nulls(self):
#        self.create_fixtures()
#        class MockBackend(BaseShippingBackend):
#            backend_name = "Fake"
#            url_namespace = "fake"
#        
#        class MockRequest():
#            user = self.user
#        
#        be = MockBackend()
#        order = be.shop.get_order(MockRequest())
#        self.assertEqual(order, None)
        
    def test_04_get_backends_from_pool(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.shipping.MockShippingBackend']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list), 1)
    
    def test_05_get_backends_from_empty_pool(self):
        self.create_fixtures()
        MODIFIERS = []
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list), 0)
    
    def test_06_get_backends_from_non_path(self):
        self.create_fixtures()
        MODIFIERS = ['blob']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_shipping_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
    
    def test_07_get_backends_from_non_module(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.IdontExist.IdontExistEither']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_shipping_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
            
    def test_08_get_backends_from_non_class(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.shipping.IdontExistEither']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_shipping_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
            
    def test_09_get_backends_cache_works(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.shipping.MockShippingBackend']
        backends_pool.USE_CACHE = True
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list), 1)
            list2 = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list2), 1)
            self.assertEqual(list,list2)
            
#    def test_10_add_shipping_costs_works(self):
#        self.create_fixtures()
#        class MockBackend(BaseShippingBackend):
#            backend_name = "Fake"
#            url_namespace = "fake"
#            
#        MODIFIERS = ['shop.tests.shipping.MockShippingBackend']
#        backends_pool.USE_CACHE = True
#        
#        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
#            be = MockBackend()
#            be.shop.add_shipping_costs(self.order, 'Test shipping', Decimal('-10'))
#            self.assertEqual(self.order.shipping_costs, Decimal('-10'))