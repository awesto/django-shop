# -*- coding: utf-8 -*-

class BaseCartModifier(object):
    """
    Price modifiers are the cart's counterpart to backends.
    It allows to implement Taxes and rebates / bulk prices in an elegant manner:
    
    Everytime the cart is refreshed (via it's update() method), the cart will 
    call all subclasses of this registered with their full path in the
    settings.SHOP_CART_MODIFIERS setting.
    """
        
    def process_cart_item(self, cart_item):
        """
        This will be called for every line item in the Cart:
        Line items typically contain: product, unit_price, quantity...
        
        Subtotal for every line (unit price * quantity) is already computed, but
        the line total is 0, and is expected to be calculated in the Cart's 
        update() method. Subtotal and total should NOT be written by this.
        
        Overrides of this method should however update cart_item.current_total, 
        since it will potentially be used by other modifiers.
        """
        field = self.get_extra_cart_item_price_field(cart_item)
        if field != None:
            price = field[1]
            cart_item.current_total = cart_item.current_total + price
            cart_item.extra_price_fields.append(field)
        return cart_item
    
    def process_cart(self, cart):
        """
        This will be called once per Cart, after every line item was treated
        The subtotal for the cart is already known, but the Total is 0.
        Like for the line items, total is expected to be calculated in the cart's
        update() method.
        
        Line items should be complete by now, so all of their fields are accessible
        
        Subtotal is accessible, but total is still 0.0. Overrides are expected to
        update cart.current_total.
        """
        field = self.get_extra_cart_price_field(cart)
        if field != None:
            price = field[1]
            cart.current_total = cart.current_total + price
            cart.extra_price_fields.append(field)
        return cart
    
    def get_extra_cart_item_price_field(self, cart_item):
        """
        Get an extra price field tuple for the current cart_item:
        
        This allows to modify the price easily, simply return a 
        ('Label', Decimal(difference)) from an override. This is expected to be
        a tuple.
        
        Implementations should use ``cart_item.current_price`` to compute their price
        difference (that is the subtotal, updated with all cart modifiers so far)
        
        A tax modifier would do something like this:
        >>> return ('taxes', Decimal(9))
        
        And a rebate modifier would do something along the lines of:
        >>> return ('rebate', Decimal(-9))
        
        More examples can be found in shop.cart.modifiers.*
        """
        return None # Does nothing by default
    
    def get_extra_cart_price_field(self, cart):
        """
        Get an extra price field tuple for the current cart:
        
        This allows to modify the price easily, simply return a 
        ('Label', Decimal(difference)) from an override. This is expected to be
        a tuple.
        
        Implementations should use ``cart.current_price`` to compute their price
        difference (that is the subtotal, updated with all cart modifiers so far)
        
        >>> return ('Taxes total', 19.00)
        """
        return None