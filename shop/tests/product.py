# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.models.productmodel import Product
from shop.models.ordermodel import Order, OrderItem
from django.test.testcases import TestCase


class ProductTestCase(TestCase):

    def setUp(self):
        self.product = Product()
        self.product.name = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()

    def test_unicode_returns_proper_stuff(self):
        ret = self.product.__unicode__()
        self.assertEqual(ret, self.product.name)

    def test_active_filter_returns_only_active_products(self):
        ret1 = len(Product.objects.active())
        # Set self.product to be active
        self.product.active = True
        self.product.save()
        ret2 = len(Product.objects.active())
        self.assertNotEqual(ret1, ret2)
        self.assertEqual(ret1, 0)
        self.assertEqual(ret2, 1)

    def test_get_name_works_properly_by_default(self):
        res = self.product.get_name()
        self.assertEqual(res, self.product.name)


class ProductStatisticsTestCase(TestCase):

    def setUp(self):
        self.product = Product()
        self.product.name = 'test'
        self.product.slug = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()

        self.product2 = Product()
        self.product2.name = 'test2'
        self.product2.slug = 'test2'
        self.product2.unit_price = Decimal('1.0')
        self.product2.save()

        self.product3 = Product()
        self.product3.name = 'test3'
        self.product3.slug = 'test3'
        self.product3.unit_price = Decimal('1.0')
        self.product3.save()

        self.order = Order()
        self.order.order_subtotal = Decimal('10')
        self.order.order_total = Decimal('10')
        self.order.shipping_cost = Decimal('0')

        self.order.shipping_address_text = 'shipping address example'
        self.order.billing_address_text = 'billing address example'
        self.order.save()

        self.orderitem1 = OrderItem()
        self.orderitem1.order = self.order
        self.orderitem1.product = self.product
        self.orderitem1.quantity = 5  # this will be the most bought
        self.orderitem1.save()

        self.orderitem2 = OrderItem()
        self.orderitem2.order = self.order
        self.orderitem2.product = self.product2
        self.orderitem2.quantity = 1  # this will be the second most
        self.orderitem2.save()

    def test_top_selling_works(self):
        res = Product.statistics.top_selling_products(10)
        self.assertNotEqual(res, None)
        self.assertEqual(len(res), 2)
        self.assertTrue(self.product3 not in res)
