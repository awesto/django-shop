import pytest
from django.db import models
from shop.models.fields import ChoiceEnum, ChoiceEnumField


class MyChoices(ChoiceEnum):
    A = 0, "My choice A"
    B = 1, "My choice B"


class MyColor(ChoiceEnum):
    RED = '#ff0000', "Pure red"
    BLUE = '#0000ff', "Pure blue"


class MyModel(models.Model):
    f = ChoiceEnumField(enum_type=MyChoices)

    class Meta:
        app_label = 'shop'
        managed = False


def test_int_enum():
    choice_a = MyChoices.A
    assert isinstance(choice_a, MyChoices)
    assert MyChoices.B.name == 'B'
    assert MyChoices.B.value == 1
    assert MyChoices.B.label == "My choice B"
    choice_b = MyChoices('B')
    assert str(choice_b) == "My choice B"
    assert MyChoices.default == MyChoices.A
    assert MyChoices.choices == [(0, "My choice A"), (1, "My choice B")]


def test_str_enum():
    red = MyColor.RED
    assert isinstance(red, MyColor)
    assert MyColor.BLUE.name == 'BLUE'
    assert MyColor.BLUE.value == '#0000ff'
    assert MyColor.BLUE.label == "Pure blue"
    assert MyColor.BLUE == MyColor('#0000ff')
    assert str(MyColor.BLUE) == "Pure blue"
    assert MyColor.choices == [('#ff0000', "Pure red"), ('#0000ff', "Pure blue")]


def test_to_python():
    f = ChoiceEnumField(enum_type=MyChoices)
    assert f.to_python(0) == MyChoices.A
    assert f.to_python('A') == MyChoices.A
    assert f.to_python(1) == MyChoices.B
    with pytest.raises(ValueError):
        f.to_python(None)
    with pytest.raises(ValueError):
        f.to_python(3)


def test_deconstruct():
    f = ChoiceEnumField(enum_type=MyChoices)
    name, path, args_, kwargs_ = f.deconstruct()
    assert name is None
    assert path == 'shop.models.fields.ChoiceEnumField'
    assert args_ == []
    assert kwargs_ == {}


def test_from_db_value():
    f = ChoiceEnumField(enum_type=MyChoices)
    assert f.from_db_value(0, None, None) is MyChoices.A
    assert f.from_db_value(1, None, None) is MyChoices.B
    assert f.from_db_value(2, None, None) is 2


def test_get_prep_value():
    f = ChoiceEnumField(enum_type=MyChoices)
    assert f.get_prep_value(MyChoices.A) is 0
    assert f.get_prep_value(MyChoices.B) is 1


def test_value_to_string():
    obj = MyModel(f=MyChoices.A)
    assert ChoiceEnumField(name='f').value_to_string(obj) == 'A'
    with pytest.raises(ValueError):
        ChoiceEnumField(name='f').value_to_string(0)
