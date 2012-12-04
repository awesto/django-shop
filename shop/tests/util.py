#-*- coding: utf-8 -*-
import sys
from decimal import Decimal
from django.conf import settings
from django.db.models.loading import cache
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test.testcases import TestCase
from shop.addressmodel.models import Address, Country
from shop.models.cartmodel import Cart, CartItem
from shop.models.productmodel import Product
from shop.util.address import get_shipping_address_from_request, \
    assign_address_to_request, get_billing_address_from_request
from shop.util.cart import get_or_create_cart
from shop.util.fields import CurrencyField
from shop.util.loader import load_class


class Mock(object):
        pass


class CurrencyFieldTestCase(TestCase):
    """
    Tests the currency field defined in the util package
    """
    def test_01_currencyfield_has_fixed_format(self):
        cf = CurrencyField(max_digits=2, decimal_places=10)
        number = cf.format_number(99.99)
        #number should *not* end up having only one decimal place
        self.assertEqual(Decimal(number), Decimal('99.99'))

    def test_02_currencyfield_has_default(self):
        cf = CurrencyField()
        default = cf.get_default()
        self.assertNotEqual(default, None)
        self.assertEqual(default, Decimal('0.0'))

    def test_03_currencyfield_can_override_default(self):
        cf = CurrencyField(default=Decimal('99.99'))
        default = cf.get_default()
        self.assertNotEqual(default, None)
        self.assertEqual(default, Decimal('99.99'))


class CartUtilsTestCase(TestCase):
    """
    Tests the cart util functions in the util package
    """

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")
        self.cart = Cart.objects.create()

        self.request = Mock()
        setattr(self.request, 'user', None)
        setattr(self.request, 'session', None)

    def tearDown(self):
        self.user.delete()
        self.cart.delete()
        del self.request

    def test_uninteresting_request_returns_none(self):
        ret = get_or_create_cart(self.request)
        self.assertEqual(ret, None)

    def test_passing_user_returns_new_cart(self):
        setattr(self.request, 'user', self.user)
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertNotEqual(ret, self.cart)

    def test_passing_user_returns_proper_cart(self):
        self.cart.user = self.user
        self.cart.save()
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {})
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertEqual(ret, self.cart)

    def test_passing_session_returns_new_cart(self):
        setattr(self.request, 'session', {})
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertNotEqual(ret, self.cart)

    def test_passing_session_returns_proper_cart(self):
        setattr(self.request, 'session', {'cart_id': self.cart.pk})
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertEqual(ret, self.cart)

    def test_anonymous_user_is_like_no_user(self):
        setattr(self.request, 'user', AnonymousUser())
        ret = get_or_create_cart(self.request)
        self.assertEqual(ret, None)

    def test_having_two_empty_carts_returns_database_cart(self):
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {'cart_id': self.cart.pk})
        database_cart = Cart.objects.create(user=self.user)
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertEqual(ret, database_cart)
        self.assertNotEqual(ret, self.cart)

    def test_having_filled_session_cart_and_empty_database_cart_returns_session_cart(self):
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {'cart_id': self.cart.pk})
        database_cart = Cart.objects.create(user=self.user)
        product = Product.objects.create(name='pizza', slug='pizza', unit_price=0)
        CartItem.objects.create(cart=self.cart, quantity=1, product=product)
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertNotEqual(ret, database_cart)
        self.assertNotEqual(ret.user, None)
        self.assertEqual(ret.user, self.user)
        self.assertEqual(ret, self.cart)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_having_empty_session_cart_and_filled_database_cart_returns_database_cart(self):
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {'cart_id': self.cart.pk})
        database_cart = Cart.objects.create(user=self.user)
        product = Product.objects.create(name='pizza', slug='pizza', unit_price=0)
        CartItem.objects.create(cart=database_cart, quantity=1, product=product)
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertEqual(ret, database_cart)
        self.assertNotEqual(ret, self.cart)

    def test_having_two_filled_carts_returns_session_cart(self):
        setattr(self.request, 'user', self.user)
        setattr(self.request, 'session', {'cart_id': self.cart.pk})
        database_cart = Cart.objects.create(user=self.user)
        product = Product.objects.create(name='pizza', slug='pizza', unit_price=0)
        CartItem.objects.create(cart=database_cart, quantity=1, product=product)
        CartItem.objects.create(cart=self.cart, quantity=1, product=product)
        ret = get_or_create_cart(self.request)
        self.assertNotEqual(ret, None)
        self.assertNotEqual(ret, database_cart)
        self.assertEqual(ret, self.cart)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)


class LoaderTestCase(TestCase):
    def test_loader_without_a_name_works(self):
        class_to_load = 'shop.tests.util.Mock'
        res = load_class(class_to_load)
        self.assertEqual(res, Mock)

    def test_loader_without_a_name_works_tuple(self):
        class_to_load = tuple(['shop.tests.util.Mock', 'tests'])
        res = load_class(class_to_load)
        self.assertEqual(res, Mock)

    def test_loader_without_a_name_fails(self):
        class_to_load = 'shop.tests.IdontExist.IdontExistEither'
        self.assertRaises(ImproperlyConfigured, load_class, class_to_load)

    def test_loader_without_a_name_fails_for_wrong_classname(self):
        class_to_load = 'shop.tests.util.IdontExist'
        self.assertRaises(ImproperlyConfigured, load_class, class_to_load)

    def test_loader_without_a_name_fails_when_too_short(self):
        class_to_load = 'IdontExist'
        self.assertRaises(ImproperlyConfigured, load_class, class_to_load)


class ModelImportTestCase(TestCase):
    def test_bases_old_import_path(self):
        try:
            module = __import__('shop.models.defaults.bases', globals(),
                locals(), ['BaseProduct',])
        except ImportError:
            module = False

        self.assertTrue(hasattr(module, 'BaseProduct'),
            'Model bases could not be imported from old location!')

    def test_managers_old_import_path(self):
        try:
            module = __import__('shop.models.defaults.managers', globals(),
                locals(), ['ProductManager',])
        except ImportError:
            module = False

        self.assertTrue(hasattr(module, 'ProductManager'),
            'Model managers could not be imported from old location!')


class CircularImportTestCase(TestCase):
    """
    Test circular import when custom Product model inherits from BaseProduct
    """

    # NOTE: Deleting the modules in TestCase.setUp does not work
    def setup_app(self, app_name, product_model):
        self.app_name = app_name
        apps = list(settings.INSTALLED_APPS)
        apps.insert(0, app_name)
        settings.INSTALLED_APPS = tuple(apps)

        cache.loaded = False
        try:
            del sys.modules['shop.models.productmodel']
            del sys.modules['shop.models']
        except KeyError:
            pass

        try:
            self.product_model = settings.SHOP_PRODUCT_MODEL
        except AttributeError:
            self.product_model = '!'
        settings.SHOP_PRODUCT_MODEL = product_model

    def tearDown(self):
        cache.loaded = False
        apps = list(settings.INSTALLED_APPS)
        apps.remove(self.app_name)
        settings.INSTALLED_APPS = tuple(apps)
        if self.product_model == '!':
            del settings.SHOP_PRODUCT_MODEL
        else:
            settings.SHOP_PRODUCT_MODEL = self.product_model

    def test_old_import_raises_exception(self):
        self.setup_app('circular_import_old',
            'circular_import_old.models.MyProduct')
        self.assertRaises(ImproperlyConfigured, cache.load_app,
            'circular_import_old')

    def test_new_import_doesnot_raise_exception(self):
        self.setup_app('circular_import_new',
            'circular_import_new.models.MyProduct')
        try:
            app = cache.load_app('circular_import_new')
        except ImproperlyConfigured:
            app = False
        self.assertTrue(app, 'Could not load app "circular_import_new"')


class AddressUtilTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test",
                                        email="test@example.com",
                                        first_name="Test",
                                        last_name="Toto")

        self.country = Country.objects.create(name="Switzerland")

        self.address = Address.objects.create(country=self.country)

        self.request = Mock()
        setattr(self.request, 'user', None)
        setattr(self.request, 'session', {})

    #==========================================================================
    # Shipping
    #==========================================================================
    def test_get_shipping_address_from_request_no_preset(self):
        # Set the user
        setattr(self.request, 'user', self.user)
        res = get_shipping_address_from_request(self.request)
        self.assertEqual(res, None)

    def test_get_shipping_address_from_request_with_preset_and_user(self):
        setattr(self.request, 'user', self.user)
        assign_address_to_request(self.request, self.address, shipping=True)
        res = get_shipping_address_from_request(self.request)
        self.assertEqual(res, self.address)

    def test_get_shipping_address_from_request_with_preset_and_session(self):
        assign_address_to_request(self.request, self.address, shipping=True)
        res = get_shipping_address_from_request(self.request)
        self.assertEqual(res, self.address)

    #==========================================================================
    # Billing
    #==========================================================================
    def test_get_billing_address_from_request_no_preset(self):
        # Set the user
        setattr(self.request, 'user', self.user)
        res = get_billing_address_from_request(self.request)
        self.assertEqual(res, None)

    def test_get_billing_address_from_request_with_preset_and_user(self):
        setattr(self.request, 'user', self.user)
        assign_address_to_request(self.request, self.address, shipping=False)
        res = get_billing_address_from_request(self.request)
        self.assertEqual(res, self.address)

    def test_get_billing_address_from_request_with_preset_and_session(self):
        assign_address_to_request(self.request, self.address, shipping=False)
        res = get_billing_address_from_request(self.request)
        self.assertEqual(res, self.address)
