# -*- coding: utf-8 -*-

""" This file contains tests for Customer behaviour. The Customer model is used
to represent shop customers; for (django-)registered customers, a
1to1-relationship to the User model is introduced."""

from django.test import Client, TestCase, RequestFactory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from shop.middleware import CustomerMiddleware
from shop.models.cart import CartModel as Cart
from shop.models.customer import CustomerModel as Customer

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
    
    # what the crap?
#    def test_create_cart_for_logged_in_users_with_customer(self):
#        """
#        Test that for logged-in users with Customer account it is used for 
#        instantiating the Cart object.
#        """
#        cart = Cart.objects.get_or_create(user=self.bart)
#        self.assertEqual(cart.customer, self.bart.customer)
#    
#    def test_create_cart_for_logged_in_users_without_customer(self):
#        """
#        Test that for logged-in users without Customer account, a new customer
#        account is created and associated with the cart as well as the user.
#        """
#        cart = Cart.objects.get_or_create(user=self.lisa)
#        customer_pk = self.lisa.customer.pk
#        self.assertEqual(cart.customer.pk, customer_pk)
#    
#    def test_create_cart_for_anonymous_user(self):
#        """
#        Test that for anonymous users, a Customer without User reference is
#        created.
#        """
#        self.cart = Cart.objects.get_or_create(session_key=self.session_key)
#        self.assertEqual(cart.session_key, self.session_key)
#        self.assertEqual(cart.user, None)

    def test_swap_customer_on_login(self):
        """
        Test that when logging in as a User with an existing Customer, that one
        is set on the request while the anonymous interim customer object is
        deleted.
        """
        from django.contrib.auth.signals import user_logged_in
        request = self.factory.post('/shop/auth/login/', follow=True)
        request.user = self.bart
        request.session = {'session_key': 'bart_swap'}
        old_customer = Customer()
        old_customer.save()
        request.customer = old_customer
        user_logged_in.send(sender=self.bart.__class__, request=request, user=self.bart)
        self.assertEqual(old_customer.pk, None)
        self.assertEqual(request.customer, self.bart.customer)
    
    def test_associate_customer_on_login(self):
        """
        Test that when logging in as a user without existing customer account,
        the anonymous interim customer object is associated with the logged-in
        user.
        """
        from django.contrib.auth.signals import user_logged_in
        request = self.factory.post('/shop/auth/login/', follow=True)
        request.user = self.lisa
        request.session = {'session_key': 'lisa_swap'}
        customer = Customer()
        request.customer = customer
        user_logged_in.send(sender=self.lisa.__class__, request=request, user=self.lisa)
        self.assertEqual(request.customer, customer)
        self.assertEqual(request.customer.user, self.lisa)
    
    def test_associate_customer_on_signup(self):
        """
        Test that when creating a new user account, the anonymous interim
        customer object is associated with the newly-created user.
        """
        pass

    def test_swap_cart_customer_on_login(self):
        """
        Test that when logging in, an existing cart's Customer reference is set
        to the new logged-in User's Customer
        """
        pass

