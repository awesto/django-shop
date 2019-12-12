import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from shop.money.money_maker import MoneyMaker
from shop.money.fields import MoneyField

EUR = MoneyMaker('EUR')


def test_deconstruct():
    f1 = MoneyField(currency='EUR', default=EUR(0))
    name, path, args, kwargs = f1.deconstruct()
    f2 = MoneyField(*args, **kwargs)
    assert f1.currency_code == f2.currency_code
    assert f1.decimal_places == f2.decimal_places
    assert f1.default == f2.default


def test_to_python():
    f = MoneyField(currency='EUR', null=True)
    assert f.to_python(3) == EUR('3')
    assert f.to_python('3.14') == EUR('3.14')
    assert f.to_python(None) == EUR()
    assert f.to_python(EUR(3)) == EUR('3')
    with pytest.raises(ValidationError):
        f.to_python('abc')


def test_get_prep_value():
    f = MoneyField(currency='EUR', null=True)
    assert f.get_prep_value(EUR('3')) == Decimal('3')


def test_from_db_value():
    f = MoneyField(currency='EUR', null=True)
    assert f.from_db_value(Decimal('3'), None, None) == EUR('3')
    assert f.from_db_value(3.45, None, None) == EUR('3.45')
    assert f.from_db_value(None, None, None) is None


def test_get_default():
    OneEuro = EUR(1)
    f = MoneyField(currency='EUR', null=True)
    assert f.get_default() is None
    f = MoneyField(currency='EUR', null=True, default=EUR())
    assert f.get_default() == EUR()
    f = MoneyField(currency='EUR', null=False, default=OneEuro)
    assert f.get_default() == OneEuro
