from __future__ import unicode_literals

from django.test import TestCase


class StartpageTest(TestCase):
    def test_get(self):
        response = self.client.get('/')
        print(response)
        self.assertEqual(response.status_code, 302)


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
