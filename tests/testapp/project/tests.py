"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import BookProduct

class ProducTest(TestCase):
    def test_app_label(self):
        self.assertEqual(BookProduct._meta.app_label, 'project')