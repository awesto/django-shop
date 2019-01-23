# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from shop.models.cart import CartModel, CartItemModel
from shop.models.customer import CustomerModel
from shop.views.catalog import ProductListView, ProductRetrieveView, AddToCartView
import pytest


@pytest.mark.django_db
def test_catalog_list(commodity_factory, rf):
    product = commodity_factory()
    request = rf.get('/catalog/')
    request.current_page = product.cms_pages.first()
    response = ProductListView.as_view()(request)
    response.render()
    assert response.data['count'] == 1
    assert response.data['next'] is None
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['product_url'] == request.path + product.slug


@pytest.mark.django_db
def test_catalog_detail(commodity_factory, customer_factory, rf):
    product = commodity_factory()
    request = rf.get('/catalog/{}'.format(product.slug))
    request.current_page = product.cms_pages.first()
    request.customer = customer_factory()
    response = ProductRetrieveView.as_view()(request, slug=product.slug)
    response.render()
    assert response.data['product_code'] == product.product_code
    assert response.data['price'] == str(product.unit_price)
    assert response.data['slug'] == product.slug


@pytest.mark.django_db
def test_get_add_to_cart(commodity_factory, customer_factory, rf):
    product = commodity_factory()
    request = rf.get(product.get_absolute_url() + '/add-to-cart')
    request.current_page = product.cms_pages.first()
    request.customer = customer_factory()
    response = AddToCartView.as_view()(request, slug=product.slug)
    response.render()
    assert response.data['quantity'] == 1
    assert response.data['unit_price'] == str(product.unit_price)
    assert response.data['product_code'] == product.product_code
    assert response.data['is_in_cart'] is False


@pytest.mark.django_db
def test_merge_with_cart(registered_customer, api_client, rf, empty_cart, commodity_factory):
    # add an item to the cart while it belongs to an anonymous customer
    assert empty_cart.num_items == 0
    CartItemModel.objects.create(cart=empty_cart, quantity=2, product=commodity_factory())
    assert empty_cart.num_items == 1

    # after logging in, the cart must be assigned to the registered customer
    login_url = reverse('shop:login')
    data = {
        'form_data': {
            'username': registered_customer.email,
            'password': 'secret',
        }
    }
    assert api_client.post(login_url, data=data, format='json').status_code == 200

    request = rf.get('/my-cart')
    request.customer = registered_customer
    cart = CartModel.objects.get_from_request(request)
    assert cart.num_items == 1
    items = cart.items.all()
    assert items[0].quantity == 2


@pytest.mark.django_db
def test_add_to_watch_list(commodity_factory, api_client, rf):
    # add a product to the cart
    product = commodity_factory()
    data = {'quantity': 1, 'product': product.id}
    response = api_client.post(reverse('shop:watch-list'), data)
    assert response.status_code == 201
    assert response.data['quantity'] == 0

    # verify that the product is in the watch-list
    request = rf.get('/my-watch-list')
    request.session = api_client.session
    request.user = AnonymousUser()
    request.customer = CustomerModel.objects.get_from_request(request)
    cart = CartModel.objects.get_from_request(request)
    assert cart.num_items == 0
    items = cart.items.all()
    assert items.count() == 1
    assert items[0].product == product
    assert items[0].quantity == 0
    return cart
