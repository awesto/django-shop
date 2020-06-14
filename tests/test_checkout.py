import pytest
from shop.forms.checkout import ShippingAddressForm
from shop.views.address import AddressEditView
from shop.views.checkout import CheckoutViewSet


@pytest.mark.django_db
def test_customer_form(registered_customer, api_rf, empty_cart):
    data = {
        'customer': {
            'salutation': "mr",
            'first_name': "John",
            'last_name': "Doe",
            'email': "john@example.com",
            'plugin_id': "1",
            'plugin_order': "1",
        },
    }
    request = api_rf.put('/shop/api/checkout/upload', data, format='json')
    request.customer = registered_customer
    response = CheckoutViewSet.as_view({'put': 'upload'})(request)
    assert response.status_code == 200
    assert registered_customer.salutation == data['customer']['salutation']
    assert registered_customer.first_name == data['customer']['first_name']
    assert registered_customer.last_name == data['customer']['last_name']
    assert registered_customer.email == data['customer']['email']


@pytest.fixture
def address_data():
    return {
        'name': "John Doe",
        'address1': "31 Orwell Road",
        'zip_code': "L41RG",
        'city': "Liverpool",
        'country': "GB",
        'plugin_id': "1",
        'plugin_order': "1",
    }


@pytest.mark.django_db
def test_new_shipping_address(registered_customer, api_rf, empty_cart):
    """
    Check that clicking on the "Add new address" returns an empty address form.
    """
    request = api_rf.get('/shop/api/shipping_address/add')
    request.customer = registered_customer
    request.user = registered_customer.user
    response = AddressEditView.as_view(form_class=ShippingAddressForm)(request, priority='add')
    assert response.status_code == 200
    assert response.data['shipping_address_form']['name'] is None
    assert response.data['shipping_address_form']['address1'] is None
    assert response.data['shipping_address_form']['zip_code'] is None
    assert response.data['shipping_address_form']['city'] is None
    assert response.data['shipping_address_form']['country'] is None


@pytest.mark.django_db
def test_add_shipping_address(registered_customer, api_rf, empty_cart, address_data):
    data = dict(shipping_address=address_data, active_priority='add')
    request = api_rf.put('/shop/api/checkout/upload', data, format='json')
    request.customer = registered_customer
    request.user = registered_customer.user
    assert registered_customer.shippingaddress_set.count() == 0
    assert registered_customer.billingaddress_set.count() == 0
    response = CheckoutViewSet.as_view({'put': 'upload'})(request)
    assert response.status_code == 200
    assert response.data['shipping_address_form']['name'] == address_data['name']
    label = "1. John Doe – 31 Orwell Road – L41RG Liverpool – United Kingdom"
    assert response.data['shipping_address_form']['siblings_summary'][0]['label'] == label
    registered_customer.refresh_from_db()
    assert registered_customer.billingaddress_set.count() == 0
    shipping_address = registered_customer.shippingaddress_set.first()
    assert shipping_address
    assert shipping_address.name == address_data['name']
    assert shipping_address.address1 == address_data['address1']
    assert shipping_address.zip_code == address_data['zip_code']
    assert shipping_address.city == address_data['city']
    assert shipping_address.country == address_data['country']


@pytest.mark.django_db
def test_delete_shipping_address(registered_customer, api_rf, empty_cart, shipping_address_factory):
    assert registered_customer.shippingaddress_set.count() == 0
    registered_customer.shippingaddress_set.add(shipping_address_factory.create(customer=registered_customer))
    registered_customer.shippingaddress_set.add(shipping_address_factory.create(customer=registered_customer))
    assert registered_customer.shippingaddress_set.count() == 2
    first_priority = registered_customer.shippingaddress_set.first().priority
    last_priority = registered_customer.shippingaddress_set.last().priority
    assert first_priority != last_priority
    request = api_rf.delete('/shop/api/shipping_address/1')
    request.customer = registered_customer
    request.user = registered_customer.user
    response = AddressEditView.as_view(form_class=ShippingAddressForm)(request, priority=first_priority)
    assert response.status_code == 200
    assert registered_customer.shippingaddress_set.count() == 1
    assert registered_customer.shippingaddress_set.first().priority == last_priority


@pytest.mark.django_db
def test_delete_last_shipping_address(registered_customer, api_rf, empty_cart, shipping_address_factory):
    registered_customer.shippingaddress_set.add(shipping_address_factory.create(customer=registered_customer))
    assert registered_customer.shippingaddress_set.count() == 1
    request = api_rf.delete('/shop/api/shipping_address/1')
    request.customer = registered_customer
    request.user = registered_customer.user
    priority = registered_customer.shippingaddress_set.first().priority
    response = AddressEditView.as_view(form_class=ShippingAddressForm)(request, priority=priority)
    assert response.status_code == 410
    assert registered_customer.shippingaddress_set.count() == 0


@pytest.mark.django_db
def test_change_shipping_address(registered_customer, api_rf, empty_cart, address_data):
    data = dict(shipping_address=address_data, active_priotity=1)
    request = api_rf.put('/shop/api/checkout/upload', data, format='json')
    request.customer = registered_customer
    response = CheckoutViewSet.as_view({'put': 'upload'})(request)
    assert response.status_code == 200
    shipping_address = registered_customer.shippingaddress_set.first()
    assert shipping_address.id == registered_customer.cart.shipping_address.id
    assert shipping_address.name == address_data['name']
    assert shipping_address.address1 == address_data['address1']
    assert shipping_address.zip_code == address_data['zip_code']
    assert shipping_address.city == address_data['city']
    assert shipping_address.country == address_data['country']
    assert registered_customer.billingaddress_set.first() is None


@pytest.mark.django_db
def test_select_shipping_address(registered_customer, api_rf, empty_cart, shipping_address_factory):
    assert registered_customer.shippingaddress_set.count() == 0
    address1 = shipping_address_factory.create(customer=registered_customer)
    registered_customer.shippingaddress_set.add(address1)
    address2 = shipping_address_factory.create(customer=registered_customer)
    registered_customer.shippingaddress_set.add(address2)
    assert registered_customer.shippingaddress_set.count() == 2
    first_priority = registered_customer.shippingaddress_set.first().priority
    last_priority = registered_customer.shippingaddress_set.last().priority
    assert first_priority != last_priority
    request = api_rf.get('/shop/api/shipping_address/0')
    request.customer = registered_customer
    request.user = registered_customer.user
    response = AddressEditView.as_view(form_class=ShippingAddressForm)(request, priority=first_priority)
    assert response.status_code == 200
    assert response.data['shipping_address_form']['name'] == address1.name
    assert response.data['shipping_address_form']['address1'] == address1.address1
    assert response.data['shipping_address_form']['zip_code'] == address1.zip_code
    assert response.data['shipping_address_form']['city'] == address1.city
    assert response.data['shipping_address_form']['country'] == address1.country
    data = dict(shipping_address=response.data['shipping_address_form'])
    data['shipping_address']['plugin_order'] = 1
    request = api_rf.put('/shop/api/shipping_address/0', data, format='json')
    request.customer = registered_customer
    request.user = registered_customer.user
    response = AddressEditView.as_view(form_class=ShippingAddressForm)(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_use_shipping_address_for_billing(registered_customer, api_rf, empty_cart, address_data):
    data = {
        'shipping_address': dict(address_data, plugin_order=1, active_priority='add'),
        'billing_address': {
            'active_priority': 'add',
            'use_primary_address': True,
            'plugin_order': 2,
        },
    }
    request = api_rf.put('/shop/api/checkout/upload', data, format='json')
    request.customer = registered_customer
    response = CheckoutViewSet.as_view({'put': 'upload'})(request)
    assert response.status_code == 200
    shipping_address = registered_customer.shippingaddress_set.first()
    assert shipping_address is not None
    billing_address = registered_customer.billingaddress_set.first()
    assert billing_address is None
    request = api_rf.get('/shop/api/checkout/digest')
    request.customer = registered_customer
    response = CheckoutViewSet.as_view({'get': 'digest'})(request)
    assert response.status_code == 200
    assert response.data['checkout_digest']['billing_address_tag'] == "Use shipping address for billing"
