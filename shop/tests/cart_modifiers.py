#-*- coding: utf-8 -*-
from __future__ import with_statement
from django.core.exceptions import ImproperlyConfigured
from shop.cart import modifiers_pool
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.tests.utils.context_managers import SettingsOverride
from unittest import TestCase

class CartModifiersTestCase(TestCase):
    
    def setUp(self):
        cart_modifiers_pool.USE_CACHE=False
    
    def test_01_cart_modifier_pool_loads_modifiers_properly(self):
        '''
        Let's add a price modifier to the settings, then load it,
        then call a method on it to make sure it works.
        '''
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.TenPercentTaxModifier']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            thelist = modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            self.assertEqual(len(thelist), 1)
            instance = thelist[0]
            self.assertTrue(hasattr(instance,'TAX_PERCENTAGE'))
            
    def test_02_cart_modifiers_pool_handles_wrong_path(self):
        MODIFIERS = ['shop2.cart.modifiers.tax_modifiers'] # wrong path
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            raised = False
            try:
                modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            except:
                raised = True
            self.assertTrue(raised)
            
    def test_03_cart_modifiers_pool_handles_wrong_module(self):
        MODIFIERS = ['shop.cart.modifiers.tax_modifiers.IdontExist']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            raised = False
            try:
                modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            except ImproperlyConfigured:
                raised = True
            self.assertTrue(raised)
            
    def test_03_cart_modifiers_pool_handles_not_a_path(self):
        MODIFIERS = ['shop']
        with SettingsOverride(SHOP_CART_MODIFIERS=MODIFIERS):
            raised = False
            try:
                modifiers_pool.cart_modifiers_pool.get_modifiers_list()
            except ImproperlyConfigured:
                raised = True
            self.assertTrue(raised)
        