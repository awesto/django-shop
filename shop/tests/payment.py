# -*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test.testcases import TestCase
from shop.backends_pool import backends_pool
from shop.models.clientmodel import Address, Client, Country
from shop.models.ordermodel import Order, OrderItem, ExtraOrderItemPriceField, \
    ExtraOrderPriceField
from shop.payment.backends.pay_on_delivery import PayOnDeliveryBackend
from shop.payment.payment_backend_base import PaymentBackendAPI
from shop.tests.utils.context_managers import SettingsOverride

EXPECTED = '''A new order was placed!

Ref: fakeref| Name: Test item| Price: 100| Q: 1| SubTot: 100| Fake extra field: 10|Tot: 110| 

Subtotal: 100
Fake Taxes: 10
Total: 120'''

class MockPaymentBackend(object):
    '''
    A simple, useless backend
    '''
    def __init__(self, shop):
        self.shop = shop
        
class NamedMockPaymentBackend(MockPaymentBackend):
    backend_name = 'Fake'
    
class ValidMockPaymentBackend(NamedMockPaymentBackend):
    url_namespace = 'fake'
    

class GeneralPaymentBackendTestCase(TestCase):
    
    def create_fixtures(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        backends_pool.USE_CACHE = False
        
    def test_01_enforcing_of_name_works(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.payment.MockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            raised = False
            
            try:
                backends_pool.get_payment_backends_list()
            except NotImplementedError:
                raised = True
            
            self.assertEqual(raised, True)

    def test_02_enforcing_of_namespace_works(self):
        self.create_fixtures()
        
        MODIFIERS = ['shop.tests.payment.NamedMockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            raised = False
            
            try:
                backends_pool.get_payment_backends_list()
            except NotImplementedError:
                raised = True
            
            self.assertEqual(raised, True)
        
    def test_03_get_order_returns_sensible_nulls(self):
        self.create_fixtures()
        
        class MockRequest():
            user = self.user
        
        be = ValidMockPaymentBackend(shop=PaymentBackendAPI())
        order = be.shop.get_order(MockRequest())
        self.assertEqual(order, None)

    def test_04_get_backends_from_pool(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.payment.ValidMockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            list = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list), 1)
    
    def test_05_get_backends_from_empty_pool(self):
        self.create_fixtures()
        MODIFIERS = []
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            list = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list), 0)
    
    def test_06_get_backends_from_non_path(self):
        self.create_fixtures()
        MODIFIERS = ['blob']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_payment_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
    
    def test_07_get_backends_from_non_module(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.IdontExist.IdontExistEither']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_payment_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
            
    def test_08_get_backends_from_non_class(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.payment.IdontExistEither']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            raised = False
            try:
                backends_pool.get_payment_backends_list()
            except ImproperlyConfigured:
                raised = True
            self.assertEqual(raised, True)
            
    def test_09_get_backends_cache_works(self):
        self.create_fixtures()
        MODIFIERS = ['shop.tests.payment.ValidMockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            backends_pool.USE_CACHE = True
            list = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list), 1)
            list2 = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list2), 1)
            self.assertEqual(list, list2)
        
class PayOnDeliveryTestCase(TestCase):
    
    def create_fixtures(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        self.user.save()
        
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
        
        # The order fixture
        
        self.order = Order()
        self.order.user = self.user
        self.order.order_subtotal = Decimal('100') # One item worth 100
        self.order.order_total = Decimal('120') # plus a test field worth 10
        self.order.status = Order.PROCESSING
        ship_address = self.address
        bill_address = self.address2
        
        self.order.shipping_name = "%s %s" %(self.address.client.user.first_name, 
                                              self.address.client.user.last_name)
        
        self.order.shipping_address = ship_address.address
        self.order.shipping_address2 = ship_address.address2
        self.order.shipping_zip_code = ship_address.zip_code
        self.order.shipping_state = ship_address.state
        self.order.shipping_country = ship_address.country.name
        
        self.order.shipping_name = "%s %s" %(self.address.client.user.first_name, 
                                              self.address.client.user.last_name)
        self.order.billing_address = bill_address.address
        self.order.billing_address2 = bill_address.address2
        self.order.billing_zip_code = bill_address.zip_code
        self.order.billing_state = bill_address.state
        self.order.billing_country = bill_address.country.name
        
        self.order.save()
        
        # Orderitems
        self.orderitem = OrderItem()
        self.orderitem.order = self.order
    
        self.orderitem.product_reference = 'fakeref'
        self.orderitem.product_name = 'Test item'
        self.orderitem.unit_price = Decimal("100")
        self.orderitem.quantity = 1
    
        self.orderitem.line_subtotal = Decimal('100')
        self.orderitem.line_total = Decimal('110')
        self.orderitem.save()
        
        eoif = ExtraOrderItemPriceField()
        eoif.order_item = self.orderitem
        eoif.label = 'Fake extra field'
        eoif.value = Decimal("10")
        eoif.save()
        
        eof = ExtraOrderPriceField()
        eof.order = self.order
        eof.label = "Fake Taxes"
        eof.value = Decimal("10")
        eof.save()
    
    def test_01_backend_returns_urls(self):
        self.create_fixtures()
        be = PayOnDeliveryBackend(shop=PaymentBackendAPI())
        urls = be.get_urls()
        self.assertNotEqual(urls,None)
        self.assertEqual(len(urls), 1)