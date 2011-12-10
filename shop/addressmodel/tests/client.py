# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from shop.addressmodel.models import Country, Address
from django.test.testcases import TestCase


class ClientTestCase(TestCase):

    def create_fixtures(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")

        self.country = Country.objects.create(name='CH')

        self.address = Address()
        self.address.client = self.client
        self.address.address = 'address'
        self.address.address2 = 'address2'
        self.address.zip_code = '1234'
        self.address.state = 'ZH'
        self.address.country = self.country
        self.address.save()

        self.address2 = Address()
        self.address2.client = self.client
        self.address2.address = '2address'
        self.address2.address2 = '2address2'
        self.address2.zip_code = '21234'
        self.address2.state = '2ZH'
        self.address2.country = self.country
        self.address2.save()

#    def test_unicode_method_works(self):
#        self.create_fixtures()
#        expected = "ClientProfile for Test Toto"
#        text = self.client.__unicode__()
#        self.assertEqual(expected, text)

    def test_unicode_method_works_for_null_user_info(self):
        self.create_fixtures()
        u = User.objects.create(username="test2",
                                email="test2@example.com")
        expected = "test2"
        text = u.__unicode__()
        self.assertEqual(expected, text)
        u.delete()
