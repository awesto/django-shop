import factory
import pytest
from pytest_factoryboy import register
from importlib import import_module
from cms.api import create_page
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from shop.models.cart import CartModel
from shop.models.defaults.customer import Customer
from shop.models.related import ProductPageModel
from shop.money import Money
from tests.testshop.models import Commodity


@pytest.fixture
def session():
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore()
    session.create()
    return session


@pytest.fixture
def api_client():
    api_client = APIClient()
    return api_client


@pytest.fixture
def api_rf():
    api_rf = APIRequestFactory()
    return api_rf


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    @classmethod
    def build(cls, **kwargs):
        return super(UserFactory, cls).build(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        user = super(UserFactory, cls).create(**kwargs)
        assert isinstance(user, get_user_model())
        assert user.is_authenticated() is True
        return user

    username = factory.Sequence(lambda n: 'uid-{}'.format(n))
    password = 'secret'


@register
class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    @classmethod
    def create(cls, **kwargs):
        customer = super(CustomerFactory, cls).create(**kwargs)
        assert isinstance(customer, Customer)
        assert isinstance(customer.user, get_user_model())
        assert customer.is_authenticated() is True
        assert customer.is_registered() is True
        return customer

    user = factory.SubFactory(UserFactory)


@pytest.fixture
def registered_customer():
    user = UserFactory(email='admin@example.com', password=make_password('secret'), is_active=True)
    customer = CustomerFactory(user=user)
    assert customer.is_registered() is True
    assert isinstance(customer.user, get_user_model())
    return customer


@register
class CommodityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commodity

    product_code = factory.Sequence(lambda n: 'art-{}'.format(n))
    unit_price = Money(1)
    slug = factory.Sequence(lambda n: 'slug-{}'.format(n))

    @classmethod
    def create(cls, **kwargs):
        product = super(CommodityFactory, cls).create(**kwargs)
        page = create_page("Catalog", 'page.html', 'en')
        ProductPageModel.objects.create(page=page, product=product)
        return product


@pytest.fixture(name='cart')
@pytest.mark.django_db
def test_add_to_cart(commodity_factory, api_client, rf):
    # add a product to the cart
    product = commodity_factory()
    data = {'quantity': 2, 'product': product.id}
    response = api_client.post(reverse('shop:cart-list'), data)
    assert response.status_code == 201
    assert response.data['quantity'] == 2
    assert response.data['unit_price'] == str(product.unit_price)
    assert response.data['line_total'] == str(data['quantity'] * product.unit_price)

    # verify that the product is in the cart
    request = rf.get('/my-cart')
    request.session = api_client.session
    request.user = AnonymousUser()
    request.customer = Customer.objects.get_from_request(request)
    cart = CartModel.objects.get_from_request(request)
    cart.update(request)
    assert cart.num_items == 1
    items = cart.items.all()
    assert items[0].product == product
    assert items[0].quantity == 2
    return cart
