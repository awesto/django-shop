# -*- coding: utf-8
from __future__ import unicode_literals

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import datetime
from shop.models.cart import CartItemModel
from shop.models.order import OrderModel
from shop.views.checkout import CheckoutViewSet
from shop.views.order import OrderView


@pytest.fixture(name='order')
@pytest.mark.django_db
def test_purchase(api_rf, empty_cart, commodity_factory):
    # fill the cart
    product = commodity_factory()
    CartItemModel.objects.create(cart=empty_cart, product=product, product_code=product.product_code, quantity=1)
    product = commodity_factory()
    CartItemModel.objects.create(cart=empty_cart, product=product, product_code=product.product_code, quantity=2)
    assert empty_cart.num_items == 2
    data = {
        'payment_method': {
            'payment_modifier': 'forward-fund-payment',
            'plugin_order': 1,
        }
    }

    # select the payment method
    request = api_rf.put('/shop/api/checkout/upload', data=data, format='json')
    request.user = empty_cart.customer.user
    request.customer = empty_cart.customer
    response = CheckoutViewSet.as_view({'put': 'upload'})(request)
    assert response.status_code == 200

    # perform the purchase
    request = api_rf.post('/shop/api/checkout/purchase')
    request.user = empty_cart.customer.user
    request.customer = empty_cart.customer
    assert request.customer.orders.count() == 0
    empty_cart.update(request)
    response = CheckoutViewSet.as_view({'post': 'purchase'})(request)
    assert response.status_code == 200
    assert 'expression' in response.data
    assert request.customer.orders.count() == 1
    order = request.customer.orders.first()
    assert order.items.count() == 2
    assert order.total == empty_cart.total
    assert order.subtotal == empty_cart.subtotal
    assert empty_cart.items.count() == 0
    return order


@pytest.mark.django_db
def test_addendum(api_rf, order):
    data = {'annotation': "client comment"}
    request = api_rf.post('/pages/order', data=data, format='json')
    request.customer = order.customer
    response = OrderView.as_view(many=False)(request, slug=order.get_number(), secret=order.secret)
    assert response.status_code == 200
    order = OrderModel.objects.get(slug=response.data['number'])
    addendum = order.extra.get('addendum')
    assert isinstance(addendum, list)
    assert isinstance(parse_datetime(addendum[0][0]), datetime)
    assert addendum[0][1] == "client comment"


@pytest.mark.django_db
def test_add_forward_fund(admin_client, order):
    assert order.status == 'awaiting_payment'
    url = reverse('admin:testshop_order_change', args=(order.pk,))
    response = admin_client.get(url)
    assert response.status_code == 200
    data = _extract_form_data(response.content)
    # add a row for an Order payment
    half_total = order.total / 2
    data.update({
        'orderpayment_set-TOTAL_FORMS': '1',
        'orderpayment_set-0-amount': str(half_total.as_decimal()),
        'orderpayment_set-0-transaction_id': 'payment-tx-id-1',
        'orderpayment_set-0-payment_method': 'forward-fund-payment',
        '_save': 'Save',
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    order.prepayment_deposited()  # mark as partially paid
    assert order.status == 'awaiting_payment'
    assert order.is_fully_paid() is False
    assert order.amount_paid == half_total
    # reload admin page for Order
    response = admin_client.get(url)
    assert response.status_code == 200
    data = _extract_form_data(response.content)
    # add a row for the second half of the payment
    half_total = order.total - half_total.__class__(half_total.as_decimal())
    data.update({
        'orderpayment_set-TOTAL_FORMS': '2',
        'orderpayment_set-1-amount': str(half_total.as_decimal()),
        'orderpayment_set-1-transaction_id': 'payment-tx-id-2',
        'orderpayment_set-1-payment_method': 'forward-fund-payment',
        '_save': 'Save',
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    order.prepayment_deposited()  # mark as fully paid
    assert order.status == 'prepayment_deposited'
    assert order.is_fully_paid() is True
    assert order.amount_paid >= order.total


def _extract_form_data(html_content):
    data = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    for input_field in soup.form.find_all(['input', 'textarea']):
        name = input_field.attrs['name']
        if not name.startswith('_'):
            data.update({name: input_field.attrs.get('value', '')})
    for select_field in soup.form.find_all('select'):
        name = select_field.attrs['name']
        for option in select_field.find_all('option'):
            if 'selected' in option.attrs:
                data.update({name: option.attrs.get('value', '')})
                break
    return data
