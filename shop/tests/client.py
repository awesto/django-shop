# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from shop.models.clientmodel import Client
from unittest import TestCase

class ClientTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test", email="test@example.com")
    
    def tearDown(self):
        self.user.delete()
    
    def test_01_shipping_and_billing_addresses_work(self):
        c = Client()
        c.user = self.user
        
        