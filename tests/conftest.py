import factory
import pytest
from pytest_factoryboy import register
from importlib import import_module
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from shop.models.defaults.customer import Customer
from shop.models.customer import VisitingCustomer, CustomerManager
from tests.testshop.models import Commodity


@pytest.fixture
def session():
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore()
    session.create()
    return session


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


@register
class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    @classmethod
    def create(cls, **kwargs):
        customer = super(CustomerFactory, cls).create(**kwargs)
        assert isinstance(customer, Customer)
        assert customer.is_authenticated() is True
        return customer

    user = factory.SubFactory(UserFactory)


@pytest.fixture
def visiting_customer():
    customer = VisitingCustomer()
    assert customer.is_registered() is False
    assert isinstance(customer.user, AnonymousUser)
    return customer


@pytest.fixture
def registered_customer():
    customer = CustomerFactory()
    assert customer.is_registered() is True
    assert isinstance(customer.user, get_user_model())
    return customer


@register
class CommodityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commodity

    product_code = factory.Sequence(lambda n: 'art-{}'.format(n))
