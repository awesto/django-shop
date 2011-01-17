'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''

class BasePriceModifier():
    '''
    Price modifiers are the cart's counterpart to backends.
    It allows to implement Taxes and rebates / bulk prices in an elegant manner
    '''
    def process_cart(self, cart):
        pass
    
    def process_cart_item(self, cart_item):
        pass