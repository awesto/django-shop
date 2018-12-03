import factory
from pytest_factoryboy import register
from django.contrib.auth import get_user_model
from shop.models.defaults.customer import Customer
from tests.testshop.models import Commodity


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    @classmethod
    def build(cls, **kwargs):
        return super(UserFactory, cls).build(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        return super(UserFactory, cls).create(**kwargs)

    username = factory.Sequence(lambda n: 'uid-{}'.format(n))


@register
class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)


@register
class CommodityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commodity

    product_code = factory.Sequence(lambda n: 'art-{}'.format(n))
