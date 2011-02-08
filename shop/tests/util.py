#-*- coding: utf-8 -*-
from decimal import Decimal
from shop.util.fields import CurrencyField
from unittest import TestCase


class UtilTestCase(TestCase):
    '''
    Tests classes in the util package
    '''
    def test_01_currencyfield_has_fixed_format(self):
        cf = CurrencyField(max_digits=2,decimal_places=1)
        number = cf.format_number(99.99)
        #number should *not* end up having only one decimal place
        self.assertEqual(Decimal(number), Decimal('99.99'))
        
    def test_02_currencyfield_has_default(self):
        cf = CurrencyField()
        default = cf.get_default()
        self.assertNotEqual(default, None)
        self.assertEqual(default, Decimal('0.0'))
        
    def test_03_currencyfield_can_override_default(self):
        cf = CurrencyField(default=Decimal('99.99'))
        default = cf.get_default()
        self.assertNotEqual(default, None)
        self.assertEqual(default, Decimal('99.99'))