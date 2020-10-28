import pytest
from decimal import Decimal

from shop.money.money_maker import MoneyMaker

from testshop.models import Commodity

EUR = MoneyMaker('EUR')


@pytest.mark.django_db
def test_field_filter(commodity_factory):

    commodity = commodity_factory(unit_price='12.34')
    assert list(Commodity.objects.filter(unit_price='12.34')) == [commodity]
    assert list(Commodity.objects.filter(unit_price=Decimal('12.34'))) == [commodity]
    assert list(Commodity.objects.filter(unit_price=EUR('12.34'))) == [commodity]
    assert list(Commodity.objects.filter(unit_price__gt='12.33')) == [commodity]
    assert list(Commodity.objects.filter(unit_price__gt=EUR('12.33'))) == [commodity]
    assert list(Commodity.objects.filter(unit_price__gt='12.34')) == []
    assert list(Commodity.objects.filter(unit_price__gte='12.34')) == [commodity]
    assert list(Commodity.objects.filter(unit_price__lt='12.35')) == [commodity]
    assert list(Commodity.objects.filter(unit_price__lt=EUR('12.35'))) == [commodity]
    assert list(Commodity.objects.filter(unit_price__lt='12.34')) == []
    assert list(Commodity.objects.filter(unit_price__lte='12.34')) == [commodity]
