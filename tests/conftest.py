import factory
from pytest_factoryboy import register
from django.contrib.auth import get_user_model
from shop.money import Money
from shop.models.defaults.customer import Customer
from tests.models import Commodity


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = "John"
    last_name = "Doe"


@register
class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)


@register
class CommodityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commodity

    unit_price = Money('12.34')
