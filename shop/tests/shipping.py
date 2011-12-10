#-*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from shop.backends_pool import backends_pool
from shop.models.ordermodel import Order
from shop.shipping.api import ShippingAPI
from shop.tests.util import Mock
from shop.tests.utils.context_managers import SettingsOverride


class MockShippingBackend(object):
    """
    A simple, useless backend
    """
    def __init__(self, shop):
        self.shop = shop


class NamedMockShippingBackend(MockShippingBackend):
    backend_name = "Fake"


class ValidMockShippingBackend(NamedMockShippingBackend):
    url_namespace = "fake"


class GeneralShippingBackendTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test',
                                        email='test@example.com',
                                        first_name='Test',
                                        last_name='Toto')
        backends_pool.use_cache = False

        self.order = Order()
        self.order.order_subtotal = Decimal('10')
        self.order.order_total = Decimal('10')
        self.order.shipping_cost = Decimal('0')

        self.order.shipping_address_text = 'shipping address example'
        self.order.billing_address_text = 'billing address example'

        self.order.save()

    def test_enforcing_of_name_works(self):
        MODIFIERS = ['shop.tests.shipping.MockShippingBackend']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            self.assertRaises(NotImplementedError,
                backends_pool.get_shipping_backends_list)

    def test_enforcing_of_namespace_works(self):
        MODIFIERS = ['shop.tests.shipping.NamedMockShippingBackend']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            self.assertRaises(NotImplementedError,
                backends_pool.get_shipping_backends_list)

    def test_get_order_returns_sensible_nulls(self):
        class MockRequest():
            user = self.user

        be = ValidMockShippingBackend(shop=ShippingAPI())
        order = be.shop.get_order(MockRequest())
        self.assertEqual(order, None)

    def test_get_backends_from_pool(self):
        MODIFIERS = ['shop.tests.shipping.ValidMockShippingBackend']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list_ = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list_), 1)

    def test_get_backends_from_empty_pool(self):
        MODIFIERS = []
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list_ = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list_), 0)

    def test_get_backends_from_non_path(self):
        MODIFIERS = ['blob']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            self.assertRaises(ImproperlyConfigured,
                backends_pool.get_shipping_backends_list)

    def test_get_backends_from_non_module(self):
        MODIFIERS = ['shop.tests.IdontExist.IdontExistEither']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            self.assertRaises(ImproperlyConfigured,
                backends_pool.get_shipping_backends_list)

    def test_get_backends_from_non_class(self):
        MODIFIERS = ['shop.tests.shipping.IdontExistEither']
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            self.assertRaises(ImproperlyConfigured,
                backends_pool.get_shipping_backends_list)

    def test_get_backends_cache_works(self):
        MODIFIERS = ['shop.tests.shipping.ValidMockShippingBackend']
        backends_pool.use_cache = True
        with SettingsOverride(SHOP_SHIPPING_BACKENDS=MODIFIERS):
            list_ = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list_), 1)
            list2 = backends_pool.get_shipping_backends_list()
            self.assertEqual(len(list2), 1)
            self.assertEqual(list_, list2)


class ShippingApiTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
            email="test@example.com")

        self.request = Mock()
        setattr(self.request, 'user', None)

        self.order = Order()
        self.order.order_subtotal = Decimal('10')
        self.order.order_total = Decimal('10')
        self.order.shipping_cost = Decimal('0')

        self.order.shipping_address_text = 'shipping address example'
        self.order.billing_address_text = 'billing address example'

        self.order.save()

        self.shipping_label = "Shipping"
        self.shipping_value = Decimal("10")

    def test_adding_shipping_costs_work(self):
        api = ShippingAPI()
        api.add_shipping_costs(self.order, self.shipping_label,
            self.shipping_value)
        self.assertEqual(self.order.shipping_costs, self.shipping_value)
        self.assertEqual(self.order.order_total, (self.order.order_subtotal +
            self.shipping_value))

    def test_adding_shipping_costs_twice_works(self):
        # That should test against #39 regressions
        api = ShippingAPI()

        api.add_shipping_costs(self.order, self.shipping_label,
            self.shipping_value)
        api.add_shipping_costs(self.order, self.shipping_label,
            self.shipping_value)

        self.assertEqual(self.order.shipping_costs, self.shipping_value)
        self.assertEqual(self.order.order_total, (self.order.order_subtotal +
            self.shipping_value))


class FlatRateShippingTestCase(TestCase):
    """Tests for ``shop.shipping.backends.flat_rate.FlatRateShipping``."""

    def test_must_be_logged_in_if_setting_is_true(self):
        with SettingsOverride(SHOP_FORCE_LOGIN=True):
            resp = self.client.get(reverse('flat'))
            self.assertEqual(resp.status_code, 302)
            self.assertTrue('accounts/login/' in resp._headers['location'][1])
            resp = self.client.get(reverse('flat_process'))
            self.assertEqual(resp.status_code, 302)
            self.assertTrue('accounts/login/' in resp._headers['location'][1])
