import pytest
from bs4 import BeautifulSoup
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import datetime
from post_office.models import Email
from shop.models.cart import CartItemModel
from shop.models.order import OrderModel, OrderItemModel
from shop.models.delivery import DeliveryModel, DeliveryItemModel
from shop.models.notification import Notify
from shop.views.checkout import CheckoutViewSet
from shop.views.order import OrderView


@pytest.fixture(name='order')
@pytest.mark.django_db
def test_purchase(api_rf, empty_cart, commodity_factory, notification_factory):
    # fill the cart
    product = commodity_factory()
    CartItemModel.objects.create(cart=empty_cart, product=product, product_code=product.product_code, quantity=1)
    product = commodity_factory()
    CartItemModel.objects.create(cart=empty_cart, product=product, product_code=product.product_code, quantity=3)
    assert empty_cart.num_items == 2
    data = {
        'payment_method': {
            'payment_modifier': 'forward-fund-payment',
            'plugin_order': 1,
        },
        'shipping_method': {
            'shipping_modifier': 'self-collection',
            'plugin_order': 2,
        }
    }

    # add notification on an order awaiting payment
    notification_factory(
        transition_target='awaiting_payment',
        notify=Notify.CUSTOMER,
        recipient=empty_cart.customer.user,
    )

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
    assert order.extra['payment_modifier'] == 'forward-fund-payment'
    assert order.extra['shipping_modifier'] == 'self-collection'
    assert empty_cart.items.count() == 0

    # check that a confirmation email has been queued
    email = Email.objects.first()
    assert email is not None
    message = email.email_message()
    assert isinstance(message, EmailMessage)
    assert product.product_name in message.body
    assert "Subtotal: {}".format(order.subtotal) in message.body
    assert "Total: {}".format(order.total) in message.body
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


@pytest.fixture(name='paid_order')
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
        '_save': "Save",
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    order.prepayment_deposited()  # mark as fully paid
    assert order.status == 'prepayment_deposited'
    assert order.is_fully_paid() is True
    assert order.amount_paid >= order.total
    return order


@pytest.mark.django_db
def test_fulfill_order_partially(admin_client, paid_order):
    assert paid_order.status == 'prepayment_deposited'
    url = reverse('admin:testshop_order_change', args=(paid_order.pk,))
    response = admin_client.get(url)
    assert response.status_code == 200
    data = _extract_form_data(response.content)
    assert int(data['items-TOTAL_FORMS']) == 2
    data.update({
        '_fsmtransition-status-pick_goods': "Pick the goods",
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    assert response.url == url
    response = admin_client.get(url)
    assert response.status_code == 200
    order = OrderModel.objects.get(pk=paid_order.pk)
    assert not DeliveryModel.objects.filter(order=order).exists()
    assert order.status == 'pick_goods'
    data = _extract_form_data(response.content)
    assert int(data['items-TOTAL_FORMS']) == 2
    assert int(data['items-0-deliver_quantity']) == 1
    assert int(data['items-1-deliver_quantity']) == 3
    data.update({
        'items-0-canceled': 'checked',
        'items-1-deliver_quantity': '1',
        '_fsmtransition-status-pack_goods': "Pack the goods",
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    assert response.url == url
    order = OrderModel.objects.get(pk=paid_order.pk)
    assert DeliveryModel.objects.filter(order=order).count() == 1
    delivery = DeliveryModel.objects.filter(order=order).first()
    order_item = OrderItemModel.objects.get(pk=data['items-0-id'])
    assert order_item.canceled is True
    order_item = OrderItemModel.objects.get(pk=data['items-1-id'])
    assert order_item.canceled is False
    assert DeliveryItemModel.objects.filter(delivery=delivery).count() == 1
    delivery_item = DeliveryItemModel.objects.filter(delivery=delivery).first()
    delivery_item.item_id == order_item.id
    delivery_item.quantity == 1
    response = admin_client.get(url)
    assert response.status_code == 200
    assert order.status == 'pack_goods'
    data = _extract_form_data(response.content)
    assert int(data['delivery_set-TOTAL_FORMS']) == 1
    data.update({
        'delivery_set-0-shipping_id': 'A1',
        '_fsmtransition-status-ship_goods': "Ship the goods",
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    assert response.url == url
    delivery.refresh_from_db()
    assert delivery.get_number() == order.get_number() + " / 1"
    assert delivery.shipping_id == 'A1'
    response = admin_client.get(url)
    assert response.status_code == 200
    order = OrderModel.objects.get(pk=paid_order.pk)
    assert order.status == 'ready_for_delivery'
    data = _extract_form_data(response.content)
    data.update({
        '_fsmtransition-status-pick_goods': "Pick the goods",
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    response = admin_client.get(url)
    assert response.status_code == 200
    order = OrderModel.objects.get(pk=order.pk)
    assert order.status == 'pick_goods'
    data = _extract_form_data(response.content)
    assert int(data['items-TOTAL_FORMS']) == 2
    assert data['items-0-canceled'] == 'checked'
    assert int(data['items-0-deliver_quantity']) == 1
    assert int(data['items-1-deliver_quantity']) == 2
    data.update({
        '_fsmtransition-status-pack_goods': "Pack the goods",
    })
    response = admin_client.post(url, data)
    assert response.status_code == 302
    assert DeliveryModel.objects.filter(order=order).count() == 2
    delivery = DeliveryModel.objects.filter(order=order).last()
    assert delivery.get_number() == order.get_number() + " / 2"
    assert DeliveryItemModel.objects.filter(delivery=delivery).count() == 1
    delivery_item = DeliveryItemModel.objects.filter(delivery=delivery).first()
    delivery_item.item_id == order_item.id
    delivery_item.quantity == 2


def _extract_form_data(html_content):
    data = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    for input_field in soup.form.find_all(['input', 'textarea']):
        name = input_field.attrs['name']
        if not name.startswith('_'):
            if input_field.attrs['type'] == 'checkbox':
                value = 'checked' if 'checked' in input_field.attrs else ''
            else:
                value = input_field.attrs.get('value', '')
            data.update({name: value})
    for select_field in soup.form.find_all('select'):
        name = select_field.attrs['name']
        for option in select_field.find_all('option'):
            if 'selected' in option.attrs:
                data.update({name: option.attrs.get('value', '')})
                break
    return data
