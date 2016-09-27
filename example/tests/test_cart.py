# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient, APIRequestFactory
from cms.api import add_plugin, create_page
from shop.models.cart import CartModel
from shop.models.customer import CustomerState
from shop.models.defaults.customer import Customer
from shop.cascade.cart import ShopCartPlugin
from myshop.models.polymorphic.smartcard import SmartCard
from .test_shop import ShopTestCase


class CartTest(ShopTestCase):
    def setUp(self):
        super(CartTest, self).setUp()

        # create a page populated with Cascade elements used for checkout
        self.cart_page = create_page("Cart", 'INHERIT', 'en', parent=self.home_page,
                                    published=True, in_navigation=True)

    def add_editable_cart(self):
        """Add one GuestFormPlugin to the current page"""
        column_element = self.create_page_grid(self.cart_page)
        placeholder = self.cart_page.placeholders.get(slot='Main Content')
        editable_cart_element = add_plugin(placeholder, ShopCartPlugin, 'en', target=column_element)
        self.cart_page.publish('en')
        return editable_cart_element

    # def test_anonymous_cart(self):
    #     #editable_cart_element = self.add_editable_cart()

    def test_anonymous_cart(self):
        # before we add a product to the cart, no session shall exist
        response = self.client.get('/')
        self.assertFalse('sessionid' in response.cookies)

        # add a product anonymously
        sdhc_4gb = SmartCard.objects.get(slug="sdhc-card-4gb")
        self.add_product2cart(sdhc_4gb)

        # now a session must be assigned to the client
        response = self.client.get('/')
        self.assertTrue(settings.SESSION_COOKIE_NAME in response.cookies)
        sessionid = response.cookies[settings.SESSION_COOKIE_NAME].value

        # check that the added item is in the cart
        request = self.factory.get('/')
        self.middleware_process_request(request, sessionid)
        cart = CartModel.objects.get_from_request(request)
        self.assertEquals(cart.items.count(), 1)

        # change the quantity of our item using the REST interface
        client = APIClient()
        client.cookies = self.client.cookies
        cart_url = reverse('shop:cart-list')
        response = client.get(cart_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['total_quantity'], 1)
        self.assertEquals(response.data['num_items'], 1)
        self.assertEquals(response.data['items'][0]['quantity'], 1)
        put_data = dict(response.data['items'][0], quantity=2)
        response = client.put(put_data['url'], put_data, format='json')
        self.assertEquals(response.status_code, 200)
        response = client.get(cart_url)
        self.assertEquals(response.data['total_quantity'], 2)
        self.assertEquals(response.data['num_items'], 1)
        self.assertEquals(response.data['items'][0]['quantity'], 2)

        # move the item to the watch-list
        put_data = dict(response.data['items'][0], quantity=0)
        response = client.put(put_data['url'], put_data, format='json')
        self.assertEquals(response.status_code, 200)
        response = client.get(cart_url)
        self.assertEquals(response.data['total_quantity'], 0)
        self.assertEquals(response.data['num_items'], 0)

        # check that it is listed in the watch-list
        watch_url = reverse('shop:watch-list')
        response = client.get(watch_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['num_items'], 0)
        self.assertEquals(response.data['items'][0]['quantity'], 0)

        # move the item back to the cart
        put_data = dict(response.data['items'][0], quantity=1)
        response = client.put(put_data['url'], put_data, format='json')
        self.assertEquals(response.status_code, 200)
        response = client.get(watch_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['num_items'], 1)
        self.assertEquals(len(response.data['items']), 0)

        # and check that it is re-listed in the cart
        response = client.get(cart_url)
        self.assertEquals(response.data['total_quantity'], 1)
        self.assertEquals(response.data['num_items'], 1)
        self.assertEquals(len(response.data['items']), 1)

        # remove the item from the cart
        put_data = dict(response.data['items'][0])
        response = client.delete(put_data['url'])
        self.assertEquals(response.status_code, 204)

        # and check that the cart is empty
        response = client.get(cart_url)
        self.assertEquals(response.data['total_quantity'], 0)
        self.assertEquals(response.data['num_items'], 0)
        self.assertEquals(len(response.data['items']), 0)

    def test_merge_items(self):
        BART = {
            'username': 'bart',
            'first_name': 'Bart',
            'last_name': 'Simpson',
            'email': 'bart@thesimpsons.com',
            'password': 'trab',
        }
        bart = get_user_model().objects.create(**BART)
        bart = Customer.objects.create(user=bart, salutation='mr',
                                       recognized=CustomerState.REGISTERED)
        self.assertTrue(bart.is_registered())

        self.client.login(username='bart', password='trab')
        sessionid = self.client.session.session_key

        # Bart adds a product
        sdhc_4gb = SmartCard.objects.get(slug="sdhc-card-4gb")
        self.add_product2cart(sdhc_4gb)

        # check that the added item is in the cart
        request = self.factory.get('/')
        self.middleware_process_request(request, sessionid)
        cart = CartModel.objects.get_from_request(request)
        self.assertEquals(cart.items.count(), 1)
        self.assertEquals(cart.items.first().product.product_code, sdhc_4gb.product_code)

        self.client.logout()
        self.assertNotEquals(sessionid, self.client.session.session_key)
        sessionid = self.client.session.session_key

        # there should be no more cart now
        request = self.factory.get('/')
        self.middleware_process_request(request, sessionid)
        with self.assertRaises(CartModel.DoesNotExist):
            CartModel.objects.get_from_request(request)

        # add another item anonymously
        xtr_sdhc_16gb = SmartCard.objects.get(slug="extreme-plus-sdhc-16gb")
        self.add_product2cart(xtr_sdhc_16gb)

        # the cart should contain this item
        sessionid = self.client.session.session_key
        request = self.factory.get('/')
        self.middleware_process_request(request, sessionid)
        cart = CartModel.objects.get_from_request(request)
        self.assertEquals(cart.items.count(), 1)
        self.assertEquals(cart.items.first().product.product_code, xtr_sdhc_16gb.product_code)

        # Bart logs in again
        client = APIClient()
        client.cookies = self.client.cookies
        client.login(username='bart', password='trab')
        self.assertEquals(sessionid, client.session.session_key)

        # the cart now should contain both items
        request = APIRequestFactory().request()
        self.middleware_process_request(request, sessionid)
        cart = CartModel.objects.get_from_request(request)
        # TODO: we somehow must ensure that LoginView.login() is invoked
        # self.assertEquals(cart.items.count(), 2)
