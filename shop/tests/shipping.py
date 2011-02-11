#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from shop.shipping.shipping_backend_base import BaseShippingBackend
from unittest import TestCase

class GeneralShippingBackendTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
    
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
        order = be.shop.getOrder(MockRequest())
        self.assertNotEqual(order, None)
        self.assertEqual(len(order), 0) # Should basically be an empty list