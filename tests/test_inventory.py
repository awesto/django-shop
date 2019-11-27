from datetime import timedelta
from django.utils import timezone
from shop.conf import app_settings

import factory.fuzzy
import pytest
from pytest_factoryboy import register
from conftest import CommodityFactory
from testshop.models import MyProduct, MyProductInventory


class MyProductFactory(CommodityFactory):
    class Meta:
        model = MyProduct


@register
class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MyProductInventory

    product = factory.SubFactory(MyProductFactory)

datetime_min = timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone())
datetime_max = timezone.datetime.max.replace(tzinfo=timezone.get_current_timezone())


@pytest.mark.django_db
def test_availability(api_rf, inventory_factory):
    request = api_rf.get('/add-to-cart')
    now = timezone.now()
    earliest = now - timedelta(days=1)
    inventory = inventory_factory(earliest=earliest, quantity=10)
    availability = inventory.product.get_availability(request)
    assert availability.quantity == 10
    assert availability.earliest == earliest
    assert availability.latest == datetime_max
    assert availability.sell_short is False
    assert availability.limited_offer is False


@pytest.mark.django_db
def test_sell_short(api_rf, inventory_factory):
    request = api_rf.get('/add-to-cart')
    now = timezone.now()
    earliest = now + app_settings.SHOP_SELL_SHORT_PERIOD / 2
    inventory = inventory_factory(earliest=earliest, quantity=10)
    availability = inventory.product.get_availability(request)
    assert availability.quantity == 10
    assert availability.earliest == earliest
    assert availability.latest == datetime_max
    assert availability.sell_short is True
    assert availability.limited_offer is False


@pytest.mark.django_db
def test_limited_offer(api_rf, inventory_factory):
    request = api_rf.get('/add-to-cart')
    now = timezone.now()
    earliest = now
    latest = now + app_settings.SHOP_LIMITED_OFFER_PERIOD / 2
    inventory = inventory_factory(earliest=earliest, latest=latest, quantity=10)
    availability = inventory.product.get_availability(request)
    assert availability.quantity == 10
    assert availability.earliest == earliest
    assert availability.latest == latest
    assert availability.sell_short is False
    assert availability.limited_offer is True
