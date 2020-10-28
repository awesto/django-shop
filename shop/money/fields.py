from decimal import Decimal

from django.core.exceptions import ValidationError
from django import forms
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from shop.conf import app_settings
from shop.money.iso4217 import CURRENCIES
from shop.money.money_maker import MoneyMaker, AbstractMoney


class MoneyFieldWidget(forms.widgets.NumberInput):
    """
    Replacement for NumberInput widget adding the currency suffix.
    """
    def __init__(self, attrs=None):
        defaults = {'style': 'width: 75px; text-align: right'}
        try:
            self.currency_code = attrs.pop('currency_code')
            defaults.update(attrs)
        except (KeyError, TypeError):
            raise ValueError("MoneyFieldWidget must be instantiated with a currency_code.")
        super().__init__(defaults)

    def render(self, name, value, attrs=None, renderer=None):
        input_field = super().render(name, value, attrs, renderer)
        return format_html('{} <strong>{}</strong>', input_field, self.currency_code)


class MoneyFormField(forms.DecimalField):
    """
    Use this field type in Django Forms instead of a DecimalField, whenever a input field for
    the Money representation is required.
    """
    def __init__(self, money_class=None, **kwargs):
        if money_class is None:
            money_class = MoneyMaker()
        if not issubclass(money_class, AbstractMoney):
            raise AttributeError("Given `money_class` does not declare a valid money type")
        self.Money = money_class
        if 'widget' not in kwargs:
            kwargs['widget'] = MoneyFieldWidget(attrs={'currency_code': money_class.currency})
        super().__init__(**kwargs)

    def prepare_value(self, value):
        if isinstance(value, AbstractMoney):
            return Decimal(value)
        return value

    def to_python(self, value):
        value = super().to_python(value)
        return self.Money(value)

    def validate(self, value):
        if value.currency != self.Money.currency:
            raise ValidationError("Can not convert different Money types.")
        super().validate(Decimal(value))
        return value


class MoneyField(models.DecimalField):
    """
    A MoneyField shall be used to store money related amounts in the database, keeping track of
    the used currency. Accessing a model field of type MoneyField, returns a MoneyIn<CURRENCY> type.
    """
    description = _("Money in %(currency_code)s")

    def __init__(self, *args, **kwargs):
        self.currency_code = kwargs.pop('currency', app_settings.DEFAULT_CURRENCY)
        self.Money = MoneyMaker(self.currency_code)
        defaults = {
            'max_digits': 30,
            'decimal_places': CURRENCIES[self.currency_code][1],
        }
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()
        if kwargs['max_digits'] == 30:
            kwargs.pop('max_digits')
        if kwargs['decimal_places'] == CURRENCIES[self.currency_code][1]:
            kwargs.pop('decimal_places')
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, AbstractMoney):
            return value
        if value is None:
            return self.Money('NaN')
        value = super().to_python(value)
        return self.Money(value)

    def get_prep_value(self, value):
        # force to type Decimal by using grandparent super
        value = super(models.DecimalField, self).get_prep_value(value)
        return super().to_python(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return
        if isinstance(value, float):
            value = str(value)
        return self.Money(value)

    def get_db_prep_save(self, value, connection):
        if isinstance(value, Decimal) and value.is_nan():
            return None
        return super().get_db_prep_save(value, connection)

    def get_prep_lookup(self, lookup_type, value):
        if isinstance(value, AbstractMoney):
            if value.get_currency() != self.Money.get_currency():
                msg = "This field stores money in {}, but the lookup amount is in {}"
                raise ValueError(msg.format(value.get_currency(), self.Money.get_currency()))
            value = value.as_decimal()
        result = super().get_prep_lookup(lookup_type, value)
        return result

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        # grandparent super
        value = super(models.DecimalField, self).get_prep_value(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        widget = MoneyFieldWidget(attrs={'currency_code': self.Money.currency})
        defaults = {'form_class': MoneyFormField, 'widget': widget, 'money_class': self.Money}
        defaults.update(**kwargs)
        formfield = super().formfield(**defaults)
        return formfield
