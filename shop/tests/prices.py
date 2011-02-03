#-*- coding: utf-8 -*-
from __future__ import with_statement
from shop.cart import modifiers_pool
from shop.tests.utils.context_managers import SettingsOverride
from unittest import TestCase

class PricesTestCase(TestCase):
    
    def test_01_price_modifier_pool_loads_modifiers_properly(self):
        '''
        Let's add a price modifier to the settings, then load it,
        then call a method on it to make sure it works.
        '''
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.TenPercentTaxModifier']
        with SettingsOverride(SHOP_PRICE_MODIFIERS=MODIFIERS):
            thelist = modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            self.assertEqual(len(thelist), 1)
            instance = thelist[0]
            self.assertTrue(hasattr(instance,'TAX_PERCENTAGE'))
            