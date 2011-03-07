#-*- coding: utf-8 -*-
from shop.cart.cart_modifiers_base import BaseCartModifier
from shop.models.cartmodel import CartItemOption

class ProductOptionsModifier(BaseCartModifier):
    '''
    This modifier adds an extra field to the cart to let the lineitem "know"
    about product options and their respective price.
    '''
    def add_extra_cart_item_price_field(self, cart_item):
        '''
        This adds a list of price modifiers dependeing on the product options 
        the client selected for the current cart_item (if any)
        '''
        selected_options = CartItemOption.objects.filter(cartitem=cart_item)
        
        for selected_opt in selected_options:
            option_obj = selected_opt.option
            data = (option_obj.name, option_obj.price)
            cart_item.extra_price_fields.append(data)
        
        return cart_item