import factory.fuzzy
import pytest
from pytest_factoryboy import register
from importlib import import_module
from cms.api import create_page
from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from post_office.models import EmailTemplate
from rest_framework.test import APIClient, APIRequestFactory
from shop.models.cart import CartModel
from shop.models.address import ISO_3166_CODES
from shop.models.defaults.customer import Customer
from shop.models.defaults.address import ShippingAddress, BillingAddress
from shop.models.notification import Notification
from shop.models.related import ProductPageModel
from shop.money import Money
from testshop.models import Commodity


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
    def create(cls, **kwargs):
        user = super(UserFactory, cls).create(**kwargs)
        assert isinstance(user, get_user_model())
        if DJANGO_VERSION < (2,):
            assert user.is_authenticated() is True
        else:
            assert user.is_authenticated is True
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
        assert customer.is_authenticated is True
        assert customer.is_registered is True
        return customer

    user = factory.SubFactory(UserFactory)


@pytest.fixture
def registered_customer():
    user = UserFactory(email='admin@example.com', password=make_password('secret'), is_active=True)
    customer = CustomerFactory(user=user)
    assert customer.is_registered is True
    assert isinstance(customer.user, get_user_model())
    return customer


@pytest.fixture()
def admin_user(db, django_user_model, django_username_field):
    user = UserFactory(email='admin@example.com', password=make_password('secret'),
                       is_active=True, is_staff=True, is_superuser=True)
    return user


@pytest.fixture()
def admin_client(db, admin_user):
    from django.test.client import Client

    client = Client()
    client.login(username=admin_user.username, password='secret')
    return client


@register
class CommodityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commodity

    product_name = factory.fuzzy.FuzzyText(prefix='Product-')
    product_code = factory.Sequence(lambda n: 'article-{}'.format(n + 1))
    unit_price = Money(factory.fuzzy.FuzzyDecimal(1, 100).fuzz())
    slug = factory.fuzzy.FuzzyText(length=7)
    order = factory.Sequence(lambda n: n)
    quantity = 5

    @classmethod
    def create(cls, **kwargs):
        product = super(CommodityFactory, cls).create(**kwargs)
        page = create_page("Catalog", 'page.html', 'en')
        ProductPageModel.objects.create(page=page, product=product)
        return product


@pytest.fixture
def empty_cart(rf, api_client):
    request = rf.get('/my-cart')
    request.session = api_client.session
    request.user = AnonymousUser()
    request.customer = Customer.objects.get_or_create_from_request(request)
    request.customer.email = 'joe@example.com'
    request.customer.save()
    cart = CartModel.objects.get_from_request(request)
    cart.update(request)
    assert cart.is_empty
    assert cart.subtotal == Money(0)
    return cart


@register
class ShippingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShippingAddress

    priority = factory.Sequence(lambda n: n + 1)
    name = factory.fuzzy.FuzzyText()
    address1 = factory.fuzzy.FuzzyText()
    zip_code = factory.fuzzy.FuzzyText()
    city = factory.fuzzy.FuzzyText()
    country = factory.fuzzy.FuzzyChoice(choices=dict(ISO_3166_CODES).keys())


@register
class BillingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BillingAddress


@register
class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    subject = 'Order {{ order.number }}'
    content = '{% extends "shop/email/order-detail.txt" %}'


@register
class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    mail_template = factory.SubFactory(EmailTemplateFactory)
