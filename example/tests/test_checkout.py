# -*- coding: utf-8
from __future__ import unicode_literals

import json

from django import VERSION as DJANGO_VERSION
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.http import QueryDict

from cms.api import add_plugin, create_page
from bs4 import BeautifulSoup

from shop.cascade.checkout import (
    GuestFormPlugin, CustomerFormPlugin, CheckoutAddressPlugin,
    PaymentMethodFormPlugin, ShippingMethodFormPlugin, RequiredFormFieldsPlugin,
    ExtraAnnotationFormPlugin, AcceptConditionPlugin)
from shop.models.cart import CartModel
from myshop.models import SmartCard
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

        plugin_id_input = customer_form.find('input', {'id': 'customer_plugin_id'})
        plugin_order_input = customer_form.find('input', {'id': 'customer_plugin_order'})

        data = {'customer': {'salutation': "mr", 'email': "bart@simpson.name", 'first_name': "Bart",
                             'last_name': "Simpson", 'plugin_id': plugin_id_input['value'],
                             'plugin_order': plugin_order_input['value']}}
        url = reverse('shop:checkout-upload')
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # check if Bart changed his email address
        bart = get_user_model().objects.get(username='bart')
        self.assertEqual("bart@simpson.name", bart.email)
        self.assertEqual("Mr.", bart.customer.get_salutation_display())

    def test_address_forms(self):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')

        # add shipping address to checkout page
        address_form_element = add_plugin(placeholder, CheckoutAddressPlugin, 'en',
                                          target=self.column_element)
        address_form_element.glossary = {'address_form': 'shipping', 'render_type': 'form'}
        address_form_element.save()

        # add billing address to checkout page
        address_form_element = add_plugin(placeholder, CheckoutAddressPlugin, 'en',
                                          target=self.column_element)
        address_form_element.glossary = {'address_form': 'billing', 'render_type': 'form',
                                         'multi_addr': 'on', 'allow_use_primary': 'on'}
        address_form_element.save()

        self.checkout_page.publish('en')
        url = self.checkout_page.get_absolute_url()

        # login as Bart
        self.client.login(username='bart', password='trab')
        self.fill_cart()

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        shipping_address_form = soup.find('form', {'name': 'shipping_address_form'})
        self.assertIsNotNone(shipping_address_form)
        billing_address_form = soup.find('form', {'name': 'billing_address_form'})
        self.assertIsNotNone(billing_address_form)

        shipping_plugin_id_input = shipping_address_form.find('input', {'id': 'shippingaddress_plugin_id'})
        shipping_plugin_order_input = shipping_address_form.find('input', {'id': 'shippingaddress_plugin_order'})
        billing_plugin_id_input = billing_address_form.find('input', {'id': 'billingaddress_plugin_order'})
        billing_plugin_order_input = billing_address_form.find('input', {'id': 'billingaddress_plugin_order'})

        data = {
            'shipping_address': {
                'active_priority': 'add',
                'name': "Bart Simpson", 'address1': "Park Ave.", 'address2': "",
                'zip_code': "SF123", 'city': "Springfield", 'country': "US",
                'plugin_id': shipping_plugin_id_input['value'],
                'plugin_order': shipping_plugin_order_input['value']},
            'billing_address': {
                'use_primary_address': True,
                'plugin_id': billing_plugin_id_input['value'],
                'plugin_order': billing_plugin_order_input['value']}
        }
        empty_field = None if DJANGO_VERSION >= (1, 11) else ''

        url = reverse('shop:checkout-upload')
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content.decode('utf-8'))
        self.assertIn('shipping_address_form', payload)
        self.assertIn('billing_address_form', payload)

        # check if Bart changed his address and zip code
        bart = get_user_model().objects.get(username='bart')
        self.assertIsNotNone(bart.customer)
        self.assertEqual("Mr.", bart.customer.get_salutation_display())
        address = bart.customer.shippingaddress_set.first()
        self.assertEqual(address.name, "Bart Simpson")
        self.assertEqual(address.address1, "Park Ave.")
        self.assertEqual(address.address2, empty_field)
        self.assertEqual(address.city, "Springfield")
        self.assertEqual(address.country, "US")
        self.assertFalse(bart.customer.billingaddress_set.exists())

        # try with a different billing address
        data['billing_address'] = {
            'use_shipping_address': False,
            'active_priority': 'add',
            'name': None, 'address1': None, 'address2': None, 'zip_code': None,
            'city': None, 'country': None,
            'plugin_id': billing_plugin_id_input['value'],
            'plugin_order': billing_plugin_order_input['value']
        }
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 422)
        response = json.loads(response.content.decode('utf-8'))
        self.assertIn('billing_address_form', response)
        self.assertIsInstance(response['billing_address_form'], dict)
        errors = response['billing_address_form']
        self.assertTrue('address1' in errors and 'country' in errors and 'city' in errors and
                        'name' in errors and 'zip_code' in errors)

    def any_method_plugin(self, form_plugin, method_name, method_form_name, modifier_name, modifier_choice):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')

        # add shipping address to checkout page
        any_method_form_element = add_plugin(placeholder, form_plugin, 'en',
                                             target=self.column_element)
        any_method_form_element.glossary = {'render_type': 'form'}
        any_method_form_element.save()

        self.checkout_page.publish('en')
        url = self.checkout_page.get_absolute_url()

        # login as Bart
        self.client.login(username='bart', password='trab')
        self.fill_cart()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        method_form = soup.find('form', {'name': method_form_name})
        self.assertIsNotNone(method_form)
        prefix = method_name.replace('_', '')
        plugin_id_input = method_form.find('input', {'id': '{}_plugin_id'.format(prefix)})
        plugin_order_input = method_form.find('input', {'id': '{}_plugin_order'.format(prefix)})

        data = {
            method_name: {
                modifier_name: '',
                'plugin_id': plugin_id_input['value'],
                'plugin_order': plugin_order_input['value']
            },
        }
        url = reverse('shop:checkout-upload')
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 422)
        payload = json.loads(response.content.decode('utf-8'))
        self.assertIn(method_form_name, payload)
        self.assertListEqual(payload[method_form_name][modifier_name],
                             ["This field is required."])

        # retry to post the form
        data[method_name][modifier_name] = modifier_choice
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_payment_method_plugin(self):
        self.any_method_plugin(PaymentMethodFormPlugin, 'payment_method', 'payment_method_form',
                               'payment_modifier', 'pay-in-advance')

    def test_shipping_method_plugin(self):
        self.any_method_plugin(ShippingMethodFormPlugin, 'shipping_method', 'shipping_method_form',
                               'shipping_modifier', 'postal-shipping')

    def test_required_form_plugin(self):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')

        # add shipping address to checkout page
        form_element = add_plugin(placeholder, RequiredFormFieldsPlugin, 'en',
                                  target=self.column_element)
        form_element.glossary = {'render_type': 'form'}
        form_element.save()

        self.checkout_page.publish('en')
        url = self.checkout_page.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        labels = soup.find_all('label')
        expected = '*\xa0These fields are required'
        for label in labels:
            if label.string == expected:
                break
        else:
            self.fail("Expected element: <label>{}</label>".format(expected))

    def test_extra_annotation_form_plugin(self):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')

        # add extra annotation form to checkout page
        form_element = add_plugin(placeholder, ExtraAnnotationFormPlugin, 'en',
                                  target=self.column_element)
        form_element.glossary = {'render_type': 'form'}
        form_element.save()
        self.checkout_page.publish('en')

        url = self.checkout_page.get_absolute_url()

        # login as Bart
        self.client.login(username='bart', password='trab')
        self.fill_cart()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        annotation_form = soup.find('form', {'name': 'extra_annotation_form'})
        self.assertIsNotNone(annotation_form)
        plugin_id_input = annotation_form.find('input', {'id': 'extraannotation_plugin_id'})
        plugin_order_input = annotation_form.find('input', {'id': 'extraannotation_plugin_order'})

        data = {
            'extra_annotation': {
                'annotation': "Please send next Monday",
                'plugin_id': plugin_id_input['value'],
                'plugin_order': plugin_order_input['value']},
        }
        url = reverse('shop:checkout-upload')
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        cart = CartModel.objects.get(customer=self.customer_bart)
        self.assertIsNotNone(cart)
        self.assertEqual(cart.extra['annotation'], "Please send next Monday")

        # test if extra annotation is not required
        data['extra_annotation']['annotation'] = None
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_accept_condition_plugin(self):
        # create a page populated with Cascade elements used for checkout
        placeholder = self.checkout_page.placeholders.get(slot='Main Content')

        # add accept condition form plugin to checkout page
        accept_condition_element = add_plugin(placeholder, AcceptConditionPlugin, 'en',
                                              target=self.column_element)
        accept_condition_plugin = accept_condition_element.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(accept_condition_plugin, AcceptConditionPlugin)

        # edit the plugin's content
        self.assertTrue(self.client.login(username='admin', password='admin'))

        post_data = QueryDict('', mutable=True)
        post_data.update({'body': "<p>I have read the terms and conditions and agree with them.</p>"})
        request = self.factory.post('/')
        request.session = SessionStore()
        request.session.create()

        ModelForm = accept_condition_plugin.get_form(request, accept_condition_element)
        form = ModelForm(post_data, None, instance=accept_condition_element)
        self.assertTrue(form.is_valid())
        accept_condition_plugin.save_model(request, accept_condition_element, form, True)

        # publish the checkout page
        self.checkout_page.publish('en')
        self.client.logout()

        # login as Bart
        self.client.login(username='bart', password='trab')
        self.fill_cart()
        url = self.checkout_page.get_absolute_url()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # find plugin counterpart on public page
        placeholder = self.checkout_page.publisher_public.placeholders.get(slot='Main Content')
        plugin = [p for p in placeholder.cmsplugin_set.all() if p.plugin_type == 'AcceptConditionPlugin'][0]
        accept_condition_form = soup.find('form', {'name': 'accept_condition_form.plugin_{}'.format(plugin.id)})
        accept_input = accept_condition_form.find('input', {'id': 'acceptcondition_accept'})
        if DJANGO_VERSION < (1, 11):
            accept_paragraph = str(accept_input.find_next_siblings('p')[0])
            self.assertHTMLEqual(accept_paragraph, "<p>I have read the terms and conditions and agree with them.</p>")
        else:
            accept_paragraph = str(accept_input.find_next_siblings('strong')[0])
            self.assertHTMLEqual(accept_paragraph, "<strong><p>I have read the terms and conditions and agree with them.</p></strong>")

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
        response = self.client.put(checkout_upload_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 422)
        errors = json.loads(response.content.decode('utf-8'))['customer_form']
        self.assertListEqual(errors['email'],
                             ["A customer with the e-mail address 'admin@example.com' already exists.\nIf you have used this address previously, try to reset the password."])
        data['guest']['email'] = "newbie@example.com"
        response = self.client.put(checkout_upload_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
