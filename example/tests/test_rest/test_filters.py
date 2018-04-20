import mock
import cms.api
from cms.models import Page
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase

from shop.models.defaults.mapping import ProductPage
from shop.rest.filters import RecursiveCMSPagesFilterBackend

from myshop.models import Product
from myshop.models.manufacturer import Manufacturer


def create_page(name):
    page = cms.api.create_page(name, "INHERIT", "en")
    page.site_id = 1
    page.save()
    page.publish("en")
    page = page.get_public_object()
    return page


class RecursiveCMSPagesFilterBackendTest(TestCase):

    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name='Testmanufacturer')
        self.root = create_page("root")
        self.sibling = create_page("sibling")
        self.child = create_page("child")
        self.grandchild = create_page("grandchild")
        self.grandchild.move(target=self.child, pos="first-child")
        self.child.move(target=self.root, pos="first-child")

    def _create_product(self, slug):
        return Product.objects.create(product_name=slug, slug=slug, order=1, manufacturer=self.manufacturer)

    def test_products_on_child_and_grandchild(self):
        product = self._create_product("testproduct")
        product2 = self._create_product("testproduct2")
        ProductPage.objects.create(product=product, page=self.child)
        ProductPage.objects.create(product=product2, page=self.grandchild)

        request = RequestFactory().get('/')
        request.current_page = Page.objects.get(title_set__title="root", publisher_is_draft=False)
        view = mock.Mock(cms_pages_fields=['cms_pages'])

        queryset = Product.objects.all()
        backend = RecursiveCMSPagesFilterBackend()

        self.assertEqual(backend.filter_queryset(request, queryset, view).count(), 2)

    def test_product_on_sibling(self):
        product = self._create_product("testproduct")
        ProductPage.objects.create(product=product, page=self.sibling)

        request = RequestFactory().get('/')
        request.current_page = self.root
        view = mock.Mock(cms_pages_fields=['cms_pages'])

        queryset = Product.objects.all()
        backend = RecursiveCMSPagesFilterBackend()

        self.assertEqual(backend.filter_queryset(request, queryset, view).count(), 0)

    def test_checks_cms_pages_fields(self):
        request = RequestFactory().get('/')
        view = mock.Mock(cms_pages_fields='not-a-list-or-tuple')
        queryset = Product.objects.all()

        backend = RecursiveCMSPagesFilterBackend()
        self.assertRaises(ImproperlyConfigured,
                          lambda: backend.filter_queryset(request, queryset, view))
