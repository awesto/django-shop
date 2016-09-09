from django.core.urlresolvers import reverse
from django.test import TestCase

import json

from myshop.models.polymorphic.product import Product
from myshop.models.manufacturer import Manufacturer


class ProductSelectViewTest(TestCase):

    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="testmanufacturer")
        Product.objects.create(product_name="testproduct1", order=1, manufacturer=manufacturer)

    def test_finds_product_case_insensitive(self):
        response = self.client.get(reverse('shop:select-product') + "?term=Prod")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['text'], "testproduct1")

    def test_bogus_query_finds_nothing(self):
        response = self.client.get(reverse('shop:select-product') + "?term=whatever")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data['count'], 0)
