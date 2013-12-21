from django.test.testcases import TestCase
from django.template import Template
from django.template.context import Context

from ..models.productmodel import Product


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
        context = Context({})
        Template(u"{% load shop_tags %} {% products %}").render(context)
        self.assertTrue('products' in context)
        self.assertEqual(len(context['products']), 2)

    def test02_should_return_objects_given_as_argument(self):
        self._create_fixture()
        context = Context({"ps": Product.objects.filter(unit_price=42)})
        result = Template(u"{% load shop_tags %} {% products ps %}").render(context)
        self.assertTrue('products' in context)
        self.assertEqual(len(context['products']), 3)

    def test03_should_return_empty_array_if_no_objects_found(self):
        self._create_fixture()
        context = Context({"ps": Product.objects.filter(slug='non-existant-slug')})
        result = Template(u"{% load shop_tags %} {% products ps %}").render(context)
        self.assertEqual(len(context['products']), 0)
