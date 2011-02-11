# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from shop.models.clientmodel import Client, Country, Address
from unittest import TestCase

class ClientTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test", email="test@example.com")
        
        self.client = Client()
        self.client.user = self.user
        self.client.save()
        
        self.country = Country.objects.create(name='CH')
        
        self.address = Address()
        self.address.client = self.client
        self.address.address = 'address'
        self.address.address2 = 'address2'
        self.address.zip_code = '1234'
        self.address.state = 'ZH'
        self.address.country = self.country
        self.address.is_billing = False
        self.address.is_shipping = True
        self.address.save()
        
        self.address2 = Address()
        self.address2.client = self.client
        self.address2.address = '2address'
        self.address2.address2 = '2address2'
        self.address2.zip_code = '21234'
        self.address2.state = '2ZH'
        self.address2.country = self.country
        self.address2.is_billing = True
        self.address2.is_shipping = False
        self.address2.save()
    
    def tearDown(self):
        self.user.delete()
    
    def test_01_shipping_address_shortcut_works(self):
        add = self.client.shipping_address()
        self.assertEqual(add, self.address)
    
    def test_02_billing_address_shortcut_works(self):
        add = self.client.billing_address()
        self.assertEqual(add, self.address2)
        
        