# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from shop.models.clientmodel import Address, Client, Country
from shop.models.ordermodel import Order, OrderItem, ExtraOrderItemPriceField, \
    ExtraOrderPriceField
from shop.payment.backends.pay_on_delivery import PayOnDeliveryBackend
from shop.payment.payment_backend_base import BasePaymentBackend
from unittest import TestCase

EXPECTED = '''A new order was placed!

Ref: fakeref| Name: Test item| Price: 100| Q: 1| SubTot: 100| Fake extra field: 10|Tot: 110| 

Subtotal: 100
Fake Taxes: 10
Total: 120'''


class GeneralPaymentBackendTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
    
    def tearDown(self):
        self.user.delete()
    
    def test_01_enforcing_of_name_works(self):
        class MockBackend(BasePaymentBackend):
            pass
        
        raised = False
        
        try:
            MockBackend()
        except NotImplementedError:
            raised = True
        
        self.assertEqual(raised, True)
        
    def test_02_enforcing_of_namespace_works(self):
        class MockBackend(BasePaymentBackend):
            backend_name = "Fake"
        
        raised = False
        
        try:
            MockBackend()
        except NotImplementedError:
            raised = True
        
        self.assertEqual(raised, True)
        
    def test_03_get_order_returns_sensible_nulls(self):
        class MockBackend(BasePaymentBackend):
            backend_name = "Fake"
            url_namespace = "fake"
        
        class MockRequest():
            user = self.user
        
        be = MockBackend()
        order = be.shop.getOrder(MockRequest())
        self.assertNotEqual(order, None)
        self.assertEqual(len(order), 0) # Should basically be an empty list
        
        
class PayOnDeliveryTestCase(TestCase):
    
    def setUp(self):
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
        
    def tearDown(self):
        self.user.delete()
    
    def test_01_empty_order_text(self):
        be = PayOnDeliveryBackend()
        text= be._create_email_body(None)
        self.assertNotEqual(None,text)
        
    def test_02_normal_order_text(self):
        
        be = PayOnDeliveryBackend()
        text = be._create_email_body(self.order)
        self.assertEqual(EXPECTED, text)
    
    def test_03_backend_returns_urls(self):
        be = PayOnDeliveryBackend()
        urls = be.get_urls()
        self.assertNotEqual(urls,None)
        self.assertEqual(len(urls), 1)