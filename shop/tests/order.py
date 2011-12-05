# -*- coding: utf-8 -*-
from __future__ import with_statement
from decimal import Decimal
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.cartmodel import Cart, CartItem
from shop.addressmodel.models import Address, Country
from shop.models.ordermodel import Order, OrderItem, ExtraOrderPriceField, \
    OrderPayment
from shop.models.productmodel import Product
from shop.tests.util import Mock
from shop.tests.utils.context_managers import SettingsOverride
from shop.util.order import get_order_from_request, add_order_to_request

# This try except is there to let people run the tests from any project
# Not only from the provided "test" project.
SKIP_BASEPRODUCT_TEST = False
try:
    from project.models import BaseProduct, ProductVariation
except:
    SKIP_BASEPRODUCT_TEST = True


class OrderUtilTestCase(TestCase):
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

    def test_request_without_user_or_session_returns_none(self):
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, None)

    def test_request_with_session_without_order_returns_none(self):
        setattr(self.request, 'session', {})
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, None)

    def test_request_with_order_returns_order(self):
        session = {}
        session['order_id'] = self.order.id
        setattr(self.request, 'session', session)
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, self.order)

    def test_request_with_user_returns_correct_order(self):
        setattr(self.request, 'user', self.user)
        self.order.user = self.user
        self.order.save()
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, self.order)

    def test_set_order_to_session_works(self):
        setattr(self.request, 'session', {})
        add_order_to_request(self.request, self.order)
        self.assertEqual(self.request.session['order_id'], self.order.id)

    def test_set_order_to_user_works(self):
        setattr(self.request, 'user', self.user)
        add_order_to_request(self.request, self.order)
        self.assertEqual(self.order.user, self.user)

    def test_same_user_does_not_override(self):
        self.order.user = self.user
        self.order.save()
        setattr(self.request, 'user', self.user)
        add_order_to_request(self.request, self.order)
        self.assertEqual(self.order.user, self.user)

    def test_request_with_user_returns_last_order(self):
        setattr(self.request, 'user', self.user)

        order1 = Order.objects.create(user=self.user)
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, order1)

        order2 = Order.objects.create(user=self.user)
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, order2)

    def test_addresses_are_conserved_properly(self):
        session = {}
        session['order_id'] = self.order.id
        setattr(self.request, 'session', session)
        ret = get_order_from_request(self.request)
        self.assertEqual(ret, self.order)
        self.assertEqual(ret.shipping_address_text,
                        self.order.shipping_address_text)
        self.assertEqual(ret.billing_address_text,
                        self.order.billing_address_text)


class OrderTestCase(TestCase):
    def setUp(self):

        self.order = Order()
        self.order.order_subtotal = Decimal('10')
        self.order.order_total = Decimal('10')
        self.order.shipping_cost = Decimal('0')

        self.order.shipping_address_text = 'shipping address example'
        self.order.billing_address_text = 'billing address example'

        self.order.save()

    def test_order_is_completed_works(self):
        ret = self.order.is_completed()
        self.assertNotEqual(ret, Order.COMPLETED)

    def test_is_payed_works(self):
        ret = self.order.is_payed()
        self.assertEqual(ret, False)


class OrderConversionTestCase(TestCase):

    PRODUCT_PRICE = Decimal('100')
    TEN_PERCENT = Decimal(10) / Decimal(100)

    def setUp(self):
        cart_modifiers_pool.USE_CACHE = False
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
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

        #self.client.user = self.user
        #self.client.save()

        self.country = Country.objects.create(name='CH')

        self.address = Address()
        self.address.name = 'Test Toto'
        self.address.address = 'address'
        self.address.address2 = 'address2'
        self.address.zip_code = '1234'
        self.address.state = 'ZH'
        self.address.country = self.country
        self.address.is_billing = True
        self.address.is_shipping = True
        self.address.save()

        self.address2 = Address()
        self.address2.name = 'Test Toto'
        self.address2.address = '2address'
        self.address2.address2 = '2address2'
        self.address2.zip_code = '21234'
        self.address2.state = '2ZH'
        self.address2.country = self.country
        self.address2.is_billing = True
        self.address2.is_shipping = False
        self.address2.save()

    def test_create_order_from_simple_cart(self):
        """
        Let's make sure that all the info is copied over properly when using
        Order.objects.create_from_cart()
        """
        self.cart.add_product(self.product)
        self.cart.update()
        self.cart.save()

        o = Order.objects.create_from_cart(self.cart)

        self.assertNotEqual(o, None)

        ois = OrderItem.objects.filter(order=o)
        cis = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(len(ois), len(cis))

        self.assertEqual(ois[0].line_subtotal, self.PRODUCT_PRICE)
        self.assertEqual(ois[0].line_total, self.PRODUCT_PRICE)

        self.assertEqual(o.order_subtotal, self.cart.subtotal_price)
        self.assertEqual(o.order_total, self.cart.total_price)

    def test_create_order_order_items_proper_product_name(self):
        baseproduct = BaseProduct.objects.create(
                name="Table",
                unit_price=self.PRODUCT_PRICE
                )
        variation = ProductVariation.objects.create(
                baseproduct=baseproduct,
                name="white"
                )
        self.cart.add_product(variation)
        self.cart.update()
        self.cart.save()

        o = Order.objects.create_from_cart(self.cart)
        ois = OrderItem.objects.filter(order=o)
        self.assertEqual(ois[0].product_name, "Table - white")

    def test_create_order_from_taxed_cart(self):
        """
        This time assert that everything is consistent with a tax cart modifier
        """
        MODIFIERS = [
            'shop.cart.modifiers.tax_modifiers.TenPercentGlobalTaxModifier']

        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):

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

            self.assertEqual(ois[0].line_subtotal, self.PRODUCT_PRICE)
            self.assertEqual(ois[0].line_total, self.PRODUCT_PRICE)

            # Assert that there are as many extra_cart_price_fields than there
            # are extra order price fields
            e_cart_fields = self.cart.extra_price_fields
            e_order_fields = ExtraOrderPriceField.objects.filter(order=o)
            self.assertEqual(len(e_cart_fields), len(e_order_fields))

            # Check that totals match
            self.assertEqual(o.order_subtotal, self.cart.subtotal_price)
            self.assertEqual(o.order_total, self.cart.total_price)
            self.assertNotEqual(o.order_subtotal, Decimal("0"))
            self.assertNotEqual(o.order_total, Decimal("0"))

    def test_order_addresses_match_user_preferences(self):
        self.cart.add_product(self.product)
        self.cart.update()
        self.cart.save()

        self.address.is_billing = False
        self.address.save()

        o = Order.objects.create_from_cart(self.cart)
        # Must not return None, obviously
        self.assertNotEqual(o, None)

        o.set_shipping_address(self.address)
        o.set_billing_address(self.address2)

        self.assertEqual(o.shipping_address_text, self.address.as_text())
        self.assertEqual(o.billing_address_text, self.address2.as_text())

    def test_create_order_respects_product_specific_get_price_method(self):
        if SKIP_BASEPRODUCT_TEST:
            return
        baseproduct = BaseProduct.objects.create(unit_price=Decimal('10.0'))
        product = ProductVariation.objects.create(baseproduct=baseproduct)

        self.cart.add_product(product)
        self.cart.update()
        self.cart.save()
        o = Order.objects.create_from_cart(self.cart)
        oi = OrderItem.objects.filter(order=o)[0]
        self.assertEqual(oi.unit_price, baseproduct.unit_price)


class OrderPaymentTestCase(TestCase):

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

    def test_payment_sum_works(self):
        self.assertEqual(self.order.amount_payed, Decimal('-1'))

    def test_payment_sum_works_with_partial_payments(self):
        OrderPayment.objects.create(
                order=self.order,
                amount=Decimal('2'),
                transaction_id='whatever',
                payment_method='test method')
        self.assertEqual(self.order.amount_payed, 2)
        self.assertEqual(self.order.is_payed(), False)

    def test_payment_sum_works_with_full_payments(self):
        OrderPayment.objects.create(
                order=self.order,
                amount=Decimal('10'),
                transaction_id='whatever',
                payment_method='test method')
        self.assertEqual(self.order.amount_payed, 10)
        self.assertEqual(self.order.is_payed(), True)
