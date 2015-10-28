# -*- coding: utf-8 -*-

""" This file contains tests for Customer behaviour. The Customer model is used
to represent shop customers; for (django-)registered customers, a
1to1-relationship to the User model is introduced."""

from django.test import Client, TestCase, RequestFactory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in
from shop.middleware import CustomerMiddleware
from shop.models.cart import CartModel as Cart
from shop.models.customer import CustomerModel as Customer, SESSION_KEY

# ToDo: create and use test fixtures
#@modify_settings(MIDDLEWARE_CLASSES={
#    'prepend': 'django.contrib.sessions.middleware.SessionMiddleware',
#})
class CustomerTest(TestCase):
    credentials = {
        'lisa': {
            # Lisa has a django account, but no customer account yet
            'username': 'lisa',
            'password': 'asil',
        },
        'bart': {
            # Bart has a django account and a customer account
            'username': 'bart',
            'password': 'trab',
        },
        # Maggie doesn't have an account yet, but will register during checkout.
    }
    
    def setUp(self):
        self.cm = CustomerMiddleware()
        self.factory = RequestFactory()
        User = get_user_model()
        self.lisa = User.objects.create(**self.credentials['lisa'])
        self.bart = User.objects.create(**self.credentials['bart'])
        # bart should already have a Customer account
        Customer.objects.create(user=self.bart)
    
    def test_create_new_anonymous_customer(self):
        """
        Test that CustomerMiddleware creates an anonymous Customer for
        AnonymousUser.
        """
        request = self.factory.get('/', follow=True)
        request.user = AnonymousUser()
        request.session = {'session_key': 'anon1234'}
        self.cm.process_request(request)
        self.assertTrue(request.customer)
        self.assertEqual(request.customer.user, None)
    
    def test_customer_is_guest(self):
        pass #ToDo
    
    def test_set_existing_customer(self):
        """
        Test that CustomerMiddleware sets an existing Customer for logged-in
        User (Bart).
        """
        request = self.factory.get('/', follow=True)
        request.user = self.bart
        request.session = {'session_key': 'bart1234'}
        self.cm.process_request(request)
        self.assertEqual(request.customer, self.bart.customer)
    
    def test_create_new_auth_customer(self):
        """
        Test that a new authenticated Customer is created for logged-in User
        without existing Customer (Lisa).
        """
        request = self.factory.get('/', follow=True)
        request.user = self.lisa
        request.session = {'session_key': 'lisa1234'}
        self.cm.process_request(request)
        self.assertEqual(request.customer.user, self.lisa)
    
    def test_swap_customer_on_login(self):
        """
        Test that when logging in as a User with an existing Customer, that one
        is set on the request while the anonymous interim customer object is
        deleted.
        """
        request = self.factory.post('/shop/auth/login/', follow=True)
        request.user = self.bart
        old_customer = Customer()
        old_customer.save()
        request.session = {
            'session_key': 'bart_swap',
            SESSION_KEY: old_customer.pk,
        }
        request.customer = self.bart.customer
        user_logged_in.send(sender=self.bart.__class__, request=request, user=self.bart)
        try:
            Customer.objects.get_customer(request, force_unauth=True)
        except Customer.DoesNotExist:
            pass
        else:
            self.fail("""Unauthenticated customer should be deleted on login
                by a User with existing Customer""")
        self.assertEqual(request.customer, self.bart.customer)
    
    # login tests have to be massively refactored, false negatives and positives
    # encountered
    
    def test_associate_customer_on_login(self):
        """
        Test that when logging in as a user without existing customer account,
        the anonymous interim customer object is associated with the logged-in
        user.
        """
        request = self.factory.post('/shop/auth/login/', follow=True)
        request.user = self.lisa
        customer = Customer()
        customer.save()
        request.session = {
            'session_key': 'lisa_swap',
            SESSION_KEY: customer.pk,
        }
        request.customer = Customer.objects.get_customer(request)
        user_logged_in.send(sender=self.lisa.__class__, request=request, user=self.lisa)
        self.assertEqual(request.customer, customer)
        self.assertEqual(request.customer.user, self.lisa)
    
    def test_associate_customer_on_signup(self):
        """
        Test that when creating a new user account, the anonymous interim
        customer object is associated with the newly-created user.
        """
        # is this necessary, or is it handled by login logic anyway?
        pass
    
    def test_create_cart(self):
        pass
    
    def test_keep_cart_on_login(self):
        """
        Test that when logging in, an existing cart's Customer reference is set
        to the new logged-in User's Customer
        """
        request = self.factory.post('/shop/auth/login', follow=True)
        request.customer = Customer()
        request.customer.save()
        request.session = {'session_key': 'keep_cart'}
        request.user = self.bart
        old_cart = Cart.objects.get_from_request(request)
        user_logged_in.send(sender=self.bart.__class__, request=request, user=self.bart)
        new_cart = Cart.objects.get_from_request(request)
        self.assertEqual(new_cart.customer, request.customer)
        self.assertEqual(new_cart, old_cart)

