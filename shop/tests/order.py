# -*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal
from django.contrib.auth.models import User
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.cartmodel import Cart, CartItem
from shop.models.clientmodel import Client, Address, Country
from shop.models.ordermodel import Order, OrderItem, ExtraOrderPriceField
from shop.models.productmodel import Product
from shop.tests.util import Mock
from shop.tests.utils.context_managers import SettingsOverride
from shop.util.order import get_order_from_request, add_order_to_request
from django.test.testcases import TestCase

class OrderUtilTestCase(TestCase):
    def create_fixtures(self):
        self.user = User.objects.create(username="test", email="test@example.com")
        
        self.request = Mock()
        setattr(self.request, 'user', None)
        
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
        
    def test_01_request_without_user_or_session_returns_none(self):
        self.create_fixtures()
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, None)
        
    def test_02_request_with_session_without_order_returns_none(self):
        self.create_fixtures()
        setattr(self.request,'session', {})
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, None)
        
    def test_03_request_with_order_returns_order(self):
        self.create_fixtures()
        session = {}
        session['order_id'] = self.order.id
        setattr(self.request, 'session', session)
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, self.order)
    
    def test_04_request_with_user_returns_correct_order(self):
        self.create_fixtures()
        setattr(self.request, 'user', self.user)
        self.order.user = self.user
        self.order.save()
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, self.order)
        
    def test_05_set_order_to_session_works(self):
        self.create_fixtures()
        setattr(self.request,'session', {})
        add_order_to_request(self.request, self.order)
        self.assertEqual(self.request.session['order_id'], self.order.id)
        
    def test_06_set_order_to_user_works(self):
        self.create_fixtures()
        setattr(self.request,'user', self.user)
        add_order_to_request(self.request, self.order)
        self.assertEqual(self.order.user, self.user)
    
    def test_06_same_user_does_not_override(self):
        self.create_fixtures()
        self.order.user = self.user
        self.order.save()
        setattr(self.request,'user', self.user)
        add_order_to_request(self.request, self.order)
        self.assertEqual(self.order.user, self.user)
        
class OrderTestCase(TestCase):
    def create_fixtures(self):
        
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
    
    def test_01_order_is_completed_works(self):
        self.create_fixtures()
        ret = self.order.is_completed()
        self.assertNotEqual(ret, Order.COMPLETED)
    
    def test_02_is_payed_works(self):
        self.create_fixtures()
        ret = self.order.is_payed()
        self.assertEqual(ret, False)

class OrderConversionTestCase(TestCase):
    
    PRODUCT_PRICE = Decimal('100')
    TEN_PERCENT = Decimal(10) / Decimal(100)
    
    def create_fixtures(self):
        
        cart_modifiers_pool.USE_CACHE=False
        
        self.user = User.objects.create(username="test", 
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name = "Toto")
        
        self.product = Product()
        self.product.name = "TestPrduct"
        self.product.slug = "TestPrduct"
        self.product.short_description = "TestPrduct"
        self.product.long_description = "TestPrduct"
        self.product.active = True
        self.product.unit_price = self.PRODUCT_PRICE
        self.product.save()
        
        self.cart = Cart()
        self.cart.user = self.user
        self.cart.save()
        
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
        self.address.is_billing = True
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
    
    def test_01_create_order_from_simple_cart(self):
        '''
        Let's make sure that all the info is copied over properly when using
        Order.objects.create_from_cart()
        '''
        self.create_fixtures()
        self.cart.add_product(self.product)
        self.cart.update()
        self.cart.save()
        
        o = Order.objects.create_from_cart(self.cart)
        
        self.assertNotEqual(o, None)
        
        ois = OrderItem.objects.filter(order=o)
        cis = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(len(ois), len(cis))
        
        self.assertEqual(o.order_subtotal, self.cart.subtotal_price)
        self.assertEqual(o.order_total, self.cart.total_price)

    def test_02_create_order_from_taxed_cart(self):
        '''
        This time assert that everything is consistent with a tax cart modifier
        '''
        self.create_fixtures()
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.TenPercentTaxModifier']
        
        with SettingsOverride(SHOP_PRICE_MODIFIERS=MODIFIERS):

            self.cart.add_product(self.product)
            self.cart.update()
            self.cart.save()
            
            o = Order.objects.create_from_cart(self.cart,)
            
            # Must not return None, obviously
            self.assertNotEqual(o, None)
            
            # Compare all the OrderItems to all CartItems (length)
            ois = OrderItem.objects.filter(order=o)
            cis = CartItem.objects.filter(cart=self.cart)
            self.assertEqual(len(ois), len(cis))
            
            # Assert that there are as many extra_cart_price_fields than there
            # are extra order price fields
            e_cart_fields = self.cart.extra_price_fields
            e_order_fields = ExtraOrderPriceField.objects.filter(order=o)
            self.assertEqual(len(e_cart_fields), len(e_order_fields))
            
            # Check that totals match
            self.assertEqual(o.order_subtotal, self.cart.subtotal_price)
            self.assertEqual(o.order_total, self.cart.total_price)
            
    def test_03_order_addresses_match_user_preferences(self):
        self.create_fixtures()
        self.cart.add_product(self.product)
        self.cart.update()
        self.cart.save()
        
        self.address.is_billing = False
        self.address.save()
        
        o = Order.objects.create_from_cart(self.cart)
        # Must not return None, obviously
        self.assertNotEqual(o, None)
        # Check that addresses are transfered properly
        self.assertEqual(o.shipping_name, "%s %s" % (self.user.first_name, self.user.last_name))
        self.assertEqual(o.shipping_address, self.address.address)
        self.assertEqual(o.shipping_address2, self.address.address2)
        self.assertEqual(o.shipping_zip_code, self.address.zip_code)
        self.assertEqual(o.shipping_state, self.address.state)    
        self.assertEqual(o.shipping_country, self.address.country.name)
        
        self.assertEqual(o.billing_name, "%s %s" % (self.user.first_name, self.user.last_name))
        self.assertEqual(o.billing_address, self.address2.address)
        self.assertEqual(o.billing_address2, self.address2.address2)
        self.assertEqual(o.billing_zip_code, self.address2.zip_code)
        self.assertEqual(o.billing_state, self.address2.state)    
        self.assertEqual(o.billing_country, self.address2.country.name)
        
    def test_04_order_saves_item_pk_as_a_string(self):
        '''
        That's needed in case shipment or payment backends need to make fancy 
        calculations on products (i.e. shipping based on weight/size...)
        '''
        self.create_fixtures()
        self.cart.add_product(self.product)
        self.cart.update()
        self.cart.save()
        
        self.address.is_billing = False
        self.address.save()
        
        o = Order.objects.create_from_cart(self.cart)
        
        # Must not return None, obviously
        self.assertNotEqual(o, None)
        
        # take the first item from the order:
        oi = OrderItem.objects.filter(order=o)[0]
        self.assertEqual(oi.product_reference, str(self.product.id))
        
        # Lookup works?
        prod = oi.product
        self.assertEqual(prod,self.product)