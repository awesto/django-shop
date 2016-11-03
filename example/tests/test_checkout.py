# -*- coding: utf-8
from __future__ import unicode_literals

import json
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from cms.api import add_plugin, create_page
from bs4 import BeautifulSoup
from shop.cascade.checkout import GuestFormPlugin, CustomerFormPlugin, ShippingAddressFormPlugin
from myshop.models.polymorphic.smartcard import SmartCard
from .test_shop import ShopTestCase


class CheckoutTest(ShopTestCase):
    def setUp(self):
        super(CheckoutTest, self).setUp()
        self.checkout_page = create_page("Checkout", 'INHERIT', 'en', parent=self.home_page,
                                         published=True, in_navigation=True)
        self.column_element = self.create_page_grid(self.checkout_page)

    def fill_cart(self):
        # add a product to cart
        sdhc_4gb = SmartCard.objects.get(slug="sdhc-card-4gb")
        self.add_product2cart(sdhc_4gb)

    def test_customer_form(self):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')
        customer_form_element = add_plugin(placeholder, CustomerFormPlugin, 'en',
                                           target=self.column_element)
        customer_form_element.glossary = {'render_type': 'form'}
        customer_form_element.save()

        self.checkout_page.publish('en')
        url = self.checkout_page.get_absolute_url()

        # anonymous users shall not see the the customer form
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraph = soup.find('p', {'class': 'text-danger'})
        self.assertEqual("Only registered customers can access this form.", paragraph.string)

        # login as Bart
        self.client.login(username='bart', password='trab')
        self.fill_cart()

        # rendering the same URL should give another result
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        customer_form = soup.find('form', {'name': 'customer_form'})
        self.assertIsNotNone(customer_form)

        plugin_id_input = customer_form.find('input', {'id': 'id_plugin_id'})
        plugin_order_input = customer_form.find('input', {'id': 'id_plugin_order'})

        data = {'customer': {'salutation': "mr", 'email': "bart@simpson.name", 'first_name': "Bart",
                             'last_name': "Simpson", 'plugin_id': plugin_id_input['value'],
                             'plugin_order': plugin_order_input['value']}}
        url = reverse('shop:checkout-upload')
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        payload = json.loads(response.content.decode('utf-8'))

        extra_row = payload['cart']['extra_rows'][0]
        self.assertEqual("€ 0.64", extra_row['amount'])
        self.assertEqual("19% VAT incl.", extra_row['label'])

        # check if Bart changed his email address
        bart = get_user_model().objects.get(username='bart')
        self.assertEqual("bart@simpson.name", bart.email)
        self.assertEqual("Mr.", bart.customer.get_salutation_display())

    def test_address_forms(self):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')
        address_form_element = add_plugin(placeholder, ShippingAddressFormPlugin, 'en',
                                          target=self.column_element)
        address_form_element.glossary = {'render_type': 'form'}
        address_form_element.save()

        self.checkout_page.publish('en')
        url = self.checkout_page.get_absolute_url()

        # login as Bart
        self.client.login(username='bart', password='trab')
        self.fill_cart()

        # rendering the same URL should give another result
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        address_form = soup.find('form', {'name': 'shipping_address_form'})
        self.assertIsNotNone(address_form)

        plugin_id_input = address_form.find('input', {'id': 'id_plugin_id'})
        plugin_order_input = address_form.find('input', {'id': 'id_plugin_order'})

        data = {'shipping_address': {
            'name': "Bart Simpson", 'address1': "Park Ave.", 'address2': "", 'zip_code': "SF123",
            'city': "Springfield", 'country': "US", 'plugin_id': plugin_id_input['value'],
            'plugin_order': plugin_order_input['value']}}
        url = reverse('shop:checkout-upload')
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        payload = json.loads(response.content.decode('utf-8'))
        self.assertIn('shipping_address_form', payload['errors'])
        self.assertDictEqual({}, payload['errors']['shipping_address_form'])

        # check if Bart changed his address and zip code
        bart = get_user_model().objects.get(username='bart')
        self.assertIsNotNone(bart.customer)
        self.assertEqual("Mr.", bart.customer.get_salutation_display())
        address = bart.customer.shippingaddress_set.first()
        self.assertEqual("Bart Simpson", address.name)
        self.assertEqual("Park Ave.", address.address1)
        self.assertEqual("", address.address2)
        self.assertEqual("Springfield", address.city)
        self.assertEqual("US", address.country)

    def add_guestform_element(self):
        """Add one GuestFormPlugin to the current page"""
        column_element = self.create_page_grid(self.checkout_page)
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')
        guestform_element = add_plugin(placeholder, GuestFormPlugin, 'en', target=column_element)
        self.checkout_page.publish('en')
        return guestform_element

    def test_checkout_as_guest(self):
        self.fill_cart()
        guestform_element = self.add_guestform_element()

        continue_as_guest_url = reverse('shop:continue-as-guest')
        response = self.client.post(continue_as_guest_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.checkout_page.get_absolute_url())
        self.assertEquals(response.status_code, 200)
        # soup = BeautifulSoup(response.content)
        # TODO: check for form

        data = {'guest': {'email': "admin@example.com", 'plugin_id': guestform_element.pk,
                'plugin_order': '1'}}

        checkout_upload_url = reverse('shop:checkout-upload')
        response = self.client.post(checkout_upload_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
