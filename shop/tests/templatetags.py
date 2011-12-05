from django.test.testcases import TestCase

from classytags.tests import DummyParser, DummyTokens

from ..models.productmodel import Product
from ..templatetags.shop_tags import Products


class ProductsTestCase(TestCase):
    """Tests for the Products templatetag."""

    def _create_fixture(self):
        Product.objects.create(
            name='product 1', slug='product-1', active=True, unit_price=42)
        Product.objects.create(
            name='product 2', slug='product-2', active=True, unit_price=42)
        Product.objects.create(
            name='product 3', slug='product-3', active=False, unit_price=42)

    def test01_should_return_all_active_products(self):
        self._create_fixture()
        tag = Products(DummyParser(), DummyTokens())
        result = tag.get_context({}, None)
        self.assertTrue('products' in result)
        self.assertEqual(len(result['products']), 2)

    def test02_should_return_objects_given_as_argument(self):
        self._create_fixture()
        tag = Products(DummyParser(), DummyTokens())
        arg_objects = Product.objects.filter(active=False)
        result = tag.get_context({}, arg_objects)
        self.assertTrue('products' in result)
        self.assertEqual(len(result['products']), 1)

    def test03_should_return_empty_array_if_no_objects_found(self):
        self._create_fixture()
        tag = Products(DummyParser(), DummyTokens())
        arg_objects = Product.objects.filter(slug='non-existant-slug')
        result = tag.get_context({}, arg_objects)
        self.assertEqual(len(result['products']), 0)
