#-*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from shop.addressmodel.models import Country, Address
from shop.models import Product
from shop.models.cartmodel import Cart
from shop.models.ordermodel import Order
from shop.order_signals import processing
from shop.payment.api import PaymentAPI
from shop.tests.util import Mock
from shop.tests.utils.context_managers import SettingsOverride
from shop.views.checkout import CheckoutSelectionView, ThankYouView


class ShippingBillingViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        self.country = Country.objects.create(name="Switzerland")
        self.address = Address.objects.create(country=self.country)
        self.cart = Cart.objects.create()
        self.product = Product.objects.create(name='pizza', active=True, unit_price='1.25')
        self.cart.add_product(self.product)
        self.request = Mock()
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {})
        setattr(self.request, 'method', 'GET')

    def test_shipping_address_cache(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})

        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)
        res2 = view.get_shipping_address_form()
        self.assertEqual(res, res2)

    def test_shipping_address_form_post(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})

        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)

    def test_shipping_address_form_user_preset(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertNotEqual(res, None)

    def test_shipping_address_form_user_no_preset(self):
        setattr(self.request, 'user', self.user)

        address = Address.objects.create(country=self.country,
            user_shipping=self.user)
        address.save()

        view = CheckoutSelectionView(request=self.request)
        res = view.get_shipping_address_form()
        self.assertEqual(res.instance, address)

    def test_billing_address_cache(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})

        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)
        res2 = view.get_billing_address_form()
        self.assertEqual(res, res2)

    def test_billing_address_form_post(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})

        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)

    def test_billing_address_form_user_preset(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertNotEqual(res, None)

    def test_billing_address_form_user_no_preset(self):
        setattr(self.request, 'user', self.user)

        address = Address.objects.create(country=self.country,
            user_billing=self.user)
        address.save()

        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_address_form()
        self.assertEqual(res.instance, address)

    #==========================================================================
    # Billing and shipping form
    #==========================================================================
    def test_billing_and_shipping_selection_post(self):
        setattr(self.request, 'method', 'POST')
        setattr(self.request, 'POST', {})
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_and_shipping_selection_form()
        self.assertNotEqual(res, None)

    def test_billing_and_shipping_selection_get(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_and_shipping_selection_form()
        self.assertNotEqual(res, None)

    def test_billing_and_shipping_selection_cached(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.get_billing_and_shipping_selection_form()
        res2 = view.get_billing_and_shipping_selection_form()
        self.assertEqual(res, res2)

    #==========================================================================
    # Context Data
    #==========================================================================
    def test_get_context_data(self):
        setattr(self.request, 'method', 'GET')
        view = CheckoutSelectionView(request=self.request)
        ctx = view.get_context_data()
        self.assertNotEqual(ctx, None)
        self.assertNotEqual(ctx['shipping_address'], None)
        self.assertNotEqual(ctx['billing_address'], None)
        self.assertNotEqual(ctx['billing_shipping_form'], None)

    #==========================================================================
    # Login Mixin
    #==========================================================================
    def test_must_be_logged_in_if_setting_is_true(self):
        with SettingsOverride(SHOP_FORCE_LOGIN=True):
            # force creating of session
            # https://code.djangoproject.com/ticket/11475
            self.client.cookies[settings.SESSION_COOKIE_NAME] = '1'
            self.client.get(reverse('shop_welcome'))

            # save a non-empty cart in the session
            session = self.client.session
            session['cart_id'] = self.cart.pk
            session.save()

            resp = self.client.get(reverse('checkout_selection'))
            self.assertEqual(resp.status_code, 302)
            self.assertTrue('accounts/login/' in resp._headers['location'][1])

    #==========================================================================
    # Cart Required Decorator
    #==========================================================================
    def test_cart_required_redirects_on_checkout(self):
        resp = self.client.get(reverse('checkout_selection'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual('http://testserver/shop/cart/', resp._headers['location'][1])


class ShippingBillingViewOrderStuffTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        self.order = Order.objects.create()
        self.country = Country.objects.create(name='CH')
        self.s_add = Address.objects.create()  # Shipping
        self.s_add.name = 'TestName'
        self.s_add.address = 'address'
        self.s_add.city = 'city'
        self.s_add.zip_code = 'zip'
        self.s_add.state = 'state'
        self.s_add.country = self.country
        self.s_add.save()

        self.b_add = Address.objects.create()  # Billing
        self.s_add.name = 'TestName'
        self.b_add.address = 'address'
        self.b_add.city = 'city'
        self.b_add.zip_code = 'zip'
        self.b_add.state = 'state'
        self.b_add.country = self.country
        self.b_add.save()

        self.request = Mock()
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {})
        setattr(self.request, 'method', 'GET')

    def check_order_address(self):
        order = self.order
        self.assertEqual(order.shipping_address_text, self.s_add.as_text())
        self.assertEqual(order.billing_address_text, self.b_add.as_text())

    def test_assigning_to_order_from_view_works(self):
        view = CheckoutSelectionView(request=self.request)
        view.save_addresses_to_order(self.order, self.s_add, self.b_add)

        self.check_order_address()

    def test_assigning_to_order_from_view_works_with_name_and_address(self):
        self.s_add.name = 'toto'
        self.s_add.address2 = 'address2'
        self.s_add.save()
        self.b_add.name = 'toto'
        self.b_add.address2 = 'address2'
        self.b_add.save()

        view = CheckoutSelectionView(request=self.request)
        view.save_addresses_to_order(self.order, self.s_add, self.b_add)
        self.check_order_address()


class CheckoutCartToOrderTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        self.request = Mock()
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {})
        setattr(self.request, 'method', 'GET')
        self.product = Product(name='pizza', slug='pizza', unit_price='1.45', active=True)
        self.product.save()
        self.cart = Cart()
        self.cart.user = self.user
        self.cart.save()

    def test_order_created(self):
        view = CheckoutSelectionView(request=self.request)
        res = view.create_order_object_from_cart()
        self.assertEqual(res.order_total, Decimal('0'))

    def test_orders_are_created_and_cleaned_up(self):
        view = CheckoutSelectionView(request=self.request)
        # create a new order with pk 1
        old_order = view.create_order_object_from_cart()
        # create order with pk 2 so sqlite doesn't reuse pk 1
        Order.objects.create()
        # then create a different new order, from a different cart with pk 3
        # order pk 1 should be deleted here
        self.cart.add_product(self.product)
        new_order = view.create_order_object_from_cart()
        self.assertFalse(Order.objects.filter(pk=old_order.pk).exists()) # check it was deleted
        self.assertNotEqual(old_order.order_total, new_order.order_total)

    def test_processing_signal(self):
        view = CheckoutSelectionView(request=self.request)

        order_from_signal = []
        def receiver(sender, order=None, **kwargs):
            order_from_signal.append(order)

        processing.connect(receiver)
        res = view.create_order_object_from_cart()

        self.assertIs(res, order_from_signal[0])


class ThankYouViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        self.request = Mock()
        self.order = Order.objects.create(user=self.user, order_total=10)
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {})
        setattr(self.request, 'method', 'GET')

    def test_get_context_gives_correct_order(self):
        # first send the order through the payment API
        PaymentAPI().confirm_payment(self.order, 10, 'None', 'magic payment')
        # then call the view
        view = ThankYouView(request=self.request)
        self.assertNotEqual(view, None)
        res = view.get_context_data()
        self.assertNotEqual(res, None)
        # refresh self.order from db (it was saved in the view)
        self.order = Order.objects.get(pk=self.order.pk)
        self.assertEqual(self.order.status, Order.COMPLETED)
        ctx_order = res.get('order', None)
        self.assertNotEqual(ctx_order, None)
        self.assertEqual(ctx_order, self.order)
