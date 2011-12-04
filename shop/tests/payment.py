# -*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from shop.backends_pool import backends_pool
from shop.addressmodel.models import Address, Country
from shop.models.ordermodel import (
    ExtraOrderItemPriceField,
    ExtraOrderPriceField,
    Order,
    OrderItem,
)
from shop.payment.backends.pay_on_delivery import PayOnDeliveryBackend
from shop.payment.api import PaymentAPI
from shop.tests.utils.context_managers import SettingsOverride


EXPECTED = (
    'A new order was placed!'
    ' Ref: fakeref| Name: Test item| Price: 100| Q: 1| SubTot: 100|'
    ' Fake extra field: 10|Tot: 110|'
    'Subtotal: 100'
    'Fake Taxes: 10'
    'Total: 120')


class MockPaymentBackend(object):
    """
    A simple, useless backend
    """
    def __init__(self, shop):
        self.shop = shop


class NamedMockPaymentBackend(MockPaymentBackend):
    backend_name = 'Fake'


class ValidMockPaymentBackend(NamedMockPaymentBackend):
    url_namespace = 'fake'


class GeneralPaymentBackendTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        backends_pool.use_cache = False

    def test_enforcing_of_name_works(self):
        MODIFIERS = ['shop.tests.payment.MockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            self.assertRaises(NotImplementedError,
                backends_pool.get_payment_backends_list)

    def test_enforcing_of_namespace_works(self):

        MODIFIERS = ['shop.tests.payment.NamedMockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            self.assertRaises(NotImplementedError,
                backends_pool.get_payment_backends_list)

    def test_get_order_returns_sensible_nulls(self):

        class MockRequest():
            user = self.user

        be = ValidMockPaymentBackend(shop=PaymentAPI())
        order = be.shop.get_order(MockRequest())
        self.assertEqual(order, None)

    def test_get_backends_from_pool(self):
        MODIFIERS = ['shop.tests.payment.ValidMockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            list_ = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list_), 1)

    def test_get_backends_from_empty_pool(self):
        MODIFIERS = []
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            list_ = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list_), 0)

    def test_get_backends_from_non_path(self):
        MODIFIERS = ['blob']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            self.assertRaises(ImproperlyConfigured,
                backends_pool.get_payment_backends_list)

    def test_get_backends_from_non_module(self):
        MODIFIERS = ['shop.tests.IdontExist.IdontExistEither']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            self.assertRaises(ImproperlyConfigured,
                backends_pool.get_payment_backends_list)

    def test_get_backends_from_non_class(self):
        MODIFIERS = ['shop.tests.payment.IdontExistEither']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            self.assertRaises(ImproperlyConfigured,
                backends_pool.get_payment_backends_list)

    def test_get_backends_cache_works(self):
        MODIFIERS = ['shop.tests.payment.ValidMockPaymentBackend']
        with SettingsOverride(SHOP_PAYMENT_BACKENDS=MODIFIERS):
            backends_pool.use_cache = True
            list_ = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list_), 1)
            list2 = backends_pool.get_payment_backends_list()
            self.assertEqual(len(list2), 1)
            self.assertEqual(list_, list2)


class PayOnDeliveryTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        self.user.save()
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
        self.order.order_subtotal = Decimal('100')  # One item worth 100
        self.order.order_total = Decimal('120')  # plus a test field worth 10
        self.order.status = Order.PROCESSING
        ship_address = self.address
        bill_address = self.address2

        self.order.set_shipping_address(ship_address)
        self.order.set_billing_address(bill_address)
        self.order.save()

        # Orderitems
        self.orderitem = OrderItem()
        self.orderitem.order = self.order

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

    def test01_backend_returns_urls(self):
        be = PayOnDeliveryBackend(shop=PaymentAPI())
        urls = be.get_urls()
        self.assertNotEqual(urls, None)
        self.assertEqual(len(urls), 1)

    def test02_must_be_logged_in_if_setting_is_true(self):
        with SettingsOverride(SHOP_FORCE_LOGIN=True):
            resp = self.client.get(reverse('pay-on-delivery'))
            self.assertEqual(resp.status_code, 302)
            self.assertTrue('accounts/login/' in resp._headers['location'][1])
