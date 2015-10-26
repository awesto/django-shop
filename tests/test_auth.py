# -*- coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
import mock
from rest_framework.test import APIRequestFactory
from shop.rest.auth import PasswordResetSerializer
from shop.models.defaults.customer import Customer


class CustomerTest(TestCase):
    customers = {
        'lisa': {
            # Lisa has a Django account, but no Customer account yet
            'username': 'lisa',
            'email': 'lisa@thesimpsons.com',
            'password': 'asil',
        },
        'bart': {
            # Bart has a Django account and a Customer account
            #'username': 'bart',
            'email': 'bart@thesimpsons.com',
            #'password': 'trab',
            'salutation': 'mr',
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
        self.lisa = User.objects.create(**self.customers['lisa'])
        #self.bart = Customer.objects.create(**self.customers['bart'])
        self.factory = RequestFactory()

    def test_bart(self):
        lisa = get_user_model().objects.get(username=self.customers['lisa']['username'])
        print lisa


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
