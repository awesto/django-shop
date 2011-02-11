#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from shop.backend_base import backends_pool
from shop.shipping.shipping_backend_base import BaseShippingBackend
from shop.tests.utils.context_managers import SettingsOverride
from unittest import TestCase

class MockShippingBackend(object):
    '''
    A simple, useless backend
    '''

class GeneralShippingBackendTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        backends_pool.USE_CACHE = False
        
    def tearDown(self):
        self.user.delete()
    
    def test_01_enforcing_of_name_works(self):
        class MockBackend(BaseShippingBackend):
            pass
        
        raised = False
        
        try:
            MockBackend()
        except NotImplementedError:
            raised = True
        
        self.assertEqual(raised, True)
        
    def test_02_enforcing_of_namespace_works(self):
        class MockBackend(BaseShippingBackend):
            backend_name = "Fake"
        
        raised = False
        
        try:
            MockBackend()
        except NotImplementedError:
            raised = True
        
        self.assertEqual(raised, True)
        
    def test_03_get_order_returns_sensible_nulls(self):
        class MockBackend(BaseShippingBackend):
            backend_name = "Fake"
            url_namespace = "fake"
        
        class MockRequest():
            user = self.user
        
        be = MockBackend()
        order = be.shop.get_order(MockRequest())
        self.assertNotEqual(order, None)
        self.assertEqual(len(order), 0) # Should basically be an empty list
        
    def test_04_get_backends_from_pool(self):
        MODIFIERS = ['shop.tests.shipping.MockShippingBackend']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list), 1)
    
    def test_05_get_backends_from_empty_pool(self):
        MODIFIERS = []
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list), 0)
    
    def test_06_get_backends_from_non_path(self):
        MODIFIERS = ['blob']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_shipping_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
    
    def test_07_get_backends_from_non_module(self):
        MODIFIERS = ['shop.tests.IdontExist.IdontExistEither']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_shipping_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
            
    def test_08_get_backends_from_non_class(self):
        MODIFIERS = ['shop.tests.shipping.IdontExistEither']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_shipping_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
            
    def test_09_get_backends_cache_works(self):
        MODIFIERS = ['shop.tests.shipping.MockShippingBackend']
        backends_pool.USE_CACHE = True
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list), 1)
            list2 = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list2), 1)
            self.assertEqual(list,list2)
            