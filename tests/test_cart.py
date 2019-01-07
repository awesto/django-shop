# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from shop.models.cart import CartModel
from shop.models.customer import CustomerModel
from shop.views.cart import CartViewSet, WatchViewSet
import pytest


@pytest.mark.django_db
def test_list_cart(api_rf, cart):
    request = api_rf.get('/shop/api/cart')
    request.customer = cart.customer
    response = CartViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == 200
    assert response.data['num_items'] == 1
    assert response.data['total_quantity'] == 2
    assert response.data['subtotal'] == str(cart.subtotal)
    assert response.data['total'] == str(cart.total)


@pytest.mark.django_db
def test_unowned_cart(customer_factory, api_rf, cart):
    request = api_rf.get('/shop/api/cart')
    request.customer = customer_factory()
    response = CartViewSet.as_view({'get': 'list'})(request)
    assert response.data['num_items'] == 0


@pytest.mark.django_db
def test_change_quantity(api_rf, cart):
    product = cart.items.all()[0].product
    data = {'quantity': 3, 'product': product.id}
    request = api_rf.put('/shop/api/cart', data)
    request.customer = cart.customer
    response = CartViewSet.as_view({'put': 'update'})(request, pk=product.id)
    assert response.status_code == 200
    cart.refresh_from_db()
    assert cart.num_items == 1
    assert cart.items.all()[0].quantity == 3


@pytest.mark.django_db
def test_remove_item(api_rf, cart):
    product = cart.items.all()[0].product
    request = api_rf.delete('/shop/api/cart')
    request.customer = cart.customer
    response = CartViewSet.as_view({'delete': 'destroy'})(request, pk=product.id)
    assert response.status_code == 200
    cart.refresh_from_db()
    assert cart.num_items == 0
    assert cart.items.count() == 0


@pytest.fixture(name='watch_list')
@pytest.mark.django_db
def test_watch_cart_item(api_rf, cart):
    product = cart.items.all()[0].product
    data = {'quantity': 0, 'product': product.id}
    request = api_rf.put('/shop/api/cart', data)
    request.customer = cart.customer
    response = WatchViewSet.as_view({'put': 'update'})(request, pk=product.id)
    assert response.status_code == 200
    cart.refresh_from_db()
    assert cart.num_items == 0
    assert cart.items.all()[0].quantity == 0
    return cart


@pytest.mark.django_db
def test_add_watch_item(api_rf, watch_list):
    product = watch_list.items.all()[0].product
    data = {'quantity': 1, 'product': product.id}
    request = api_rf.put('/shop/api/cart', data)
    request.customer = watch_list.customer
    response = CartViewSet.as_view({'put': 'update'})(request, pk=product.id)
    assert response.status_code == 200
    watch_list.refresh_from_db()
    assert watch_list.num_items == 1
    assert watch_list.items.all()[0].quantity == 1
