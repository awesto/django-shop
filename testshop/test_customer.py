# -*- coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, RequestFactory
import mock
from rest_framework.test import APIRequestFactory
from shop.rest.auth import PasswordResetSerializer
from shop.models.defaults.customer import Customer
from shop.middleware import CustomerMiddleware
from shop.models.customer import VisitingCustomer


class CustomerTest(TestCase):
    USERS = {
        'lisa': {
            'username': 'lisa',
            'email': 'lisa@thesimpsons.com',
            'password': 'asil',
        },
        'bart': {
            'username': 'bart',
            'first_name': 'Bart',
            'last_name': 'Simpson',
            'email': 'bart@thesimpsons.com',
            'password':'trab',
        },
        'maggie': {
            # Maggie doesn't have an account yet, but will register during checkout
            'username': 'maggie',
            'email': 'maggie@thesimpsons.com',
            'password': 'eiggam',
            'salutation': 'n/a',
        },
        'homer': {
            # Homer does not register and buys as a guest
            'email': 'homer@thesimpsons.com',
        },
    }

    def setUp(self):
        super(CustomerTest, self).setUp()
        User = get_user_model()
        # Lisa has a Django account, but no Customer account yet
        self.lisa = User.objects.create(**self.USERS['lisa'])
        # Bart has a Django account and a Customer account
        self.bart = User.objects.create(**self.USERS['bart'])
        Customer.objects.create(user=self.bart).save()
        self.factory = RequestFactory()
        self.customer_middleware = CustomerMiddleware()

    def test_visiting_customer(self):
        """
        Check that an anonymous user creates a visiting customer.
        """
        request = self.factory.get('/', follow=True)
        request.user = AnonymousUser()
        request.session = SessionStore()
        request.session.create()
        customer = Customer.objects.get_from_request(request)
        customer.save()
        self.assertIsInstance(customer, VisitingCustomer)
        self.assertEqual(str(customer), 'Visitor')
        self.assertTrue(customer.is_anonymous())
        self.assertFalse(customer.is_authenticated())
        self.assertFalse(customer.is_recognized())
        self.assertFalse(customer.is_guest())
        self.assertFalse(customer.is_registered())
        self.assertTrue(customer.is_visitor())

    def test_unrecognized_customer(self):
        """
        Check that an anonymous user creates an unrecognized customer.
        """
        request = self.factory.get('/', follow=True)
        request.user = AnonymousUser()
        request.session = SessionStore()
        request.session.clear()
        customer = Customer.objects.get_or_create_from_request(request)
        self.assertIsInstance(customer, Customer)
        self.assertTrue(customer.is_anonymous())
        self.assertFalse(customer.is_authenticated())
        self.assertFalse(customer.is_recognized())
        self.assertFalse(customer.is_guest())
        self.assertFalse(customer.is_registered())
        self.assertFalse(customer.is_visitor())

    def test_unexpired_customer(self):
        """
        Check that an anonymous user creates an unrecognized customer using the current session-key.
        """
        request = self.factory.get('/', follow=True)
        request.user = AnonymousUser()
        request.session = SessionStore()
        request.session.create()
        customer = Customer.objects.get_or_create_from_request(request)
        self.assertIsInstance(customer, Customer)
        self.assertTrue(customer.is_anonymous())
        self.assertTrue(customer.is_expired())
        self.assertEqual(Customer.objects.decode_session_key(customer.user.username), request.session.session_key)
        customer.delete()
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(pk=customer.pk)
        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(pk=customer.pk)

    def test_authenticated_purchasing_user(self):
        """
        Check that an authenticated user creates a recognized customer able to add something to
        the cart.
        """
        lisa = get_user_model().objects.get(username='lisa')
        self.assertTrue(lisa.is_authenticated())
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(pk=lisa.pk)
        request = self.factory.get('/', follow=True)
        request.user = lisa
        request.session = SessionStore()
        request.session.create()
        customer = Customer.objects.get_or_create_from_request(request)
        self.assertIsInstance(customer, Customer)
        self.assertFalse(customer.is_anonymous())
        self.assertTrue(customer.is_authenticated())
        self.assertTrue(customer.is_recognized())
        self.assertFalse(customer.is_guest())
        self.assertTrue(customer.is_registered())
        self.assertFalse(customer.is_visitor())

    def test_authenticated_visiting_user(self):
        """
        Check that an authenticated user creates a recognized customer visiting the site.
        """
        lisa = get_user_model().objects.get(username='lisa')
        self.assertTrue(lisa.is_authenticated())
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(pk=lisa.pk)
        request = self.factory.get('/', follow=True)
        request.user = lisa
        request.session = SessionStore()
        request.session.create()
        customer = Customer.objects.get_from_request(request)
        self.assertIsInstance(customer, Customer)
        self.assertTrue(customer.is_authenticated())
        self.assertTrue(customer.is_recognized())
        self.assertTrue(customer.is_registered())

    def test_authenticated_visiting_customer(self):
        """
        Check that an authenticated user creates a recognized customer visiting the site.
        """
        bart = get_user_model().objects.get(username='bart')
        self.assertTrue(bart.is_authenticated())
        self.assertIsInstance(Customer.objects.get(pk=bart.pk), Customer)
        request = self.factory.get('/', follow=True)
        request.user = bart
        request.session = SessionStore()
        request.session.create()
        customer = Customer.objects.get_from_request(request)
        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.pk, bart.pk)
        self.assertTrue(customer.is_authenticated())
        self.assertTrue(customer.is_recognized())
        self.assertTrue(customer.is_registered())
        bart = self.USERS['bart']
        self.assertEqual(str(customer), bart['email'])
        self.assertEqual(customer.first_name, bart['first_name'])
        self.assertEqual(customer.last_name, bart['last_name'])
        self.assertEqual(customer.email, bart['email'])
        print customer.date_joined
        print customer.last_login


class PasswordResetSerializerTest(TestCase):

    def test_save(self):
        data = {'email': 'test@example.org'}
        request = APIRequestFactory().post('/', data)
        serializer = PasswordResetSerializer(data=data, context={
            'request': request,
        })
        self.assertTrue(serializer.is_valid())
        serializer.reset_form = mock.Mock()
        serializer.save()
        serializer.reset_form.save.assert_called_with(
            use_https=False,
            from_email='webmaster@localhost',
            request=request,
            subject_template_name=u'shop/email/reset-password-subject.txt',
            email_template_name='shop/email/reset-password-body.txt',
        )
