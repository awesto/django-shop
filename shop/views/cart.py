# -*- coding: utf-8 -*-
from models.cartmodel import Cart
from models.productmodel import Product

def add_product_to_cart(request, product_id):
    '''
    Adds a product passed in parameter (via its ID) to the current user's 
    shopping basket.
    '''
    shopping_cart_id = request.user.get('shopping_cart', False)
    if not shopping_cart_id:
        shopping_cart_id = request.session.get('shopping_cart', False)
    if not shopping_cart_id:
        #TODO Handle the no user + no session case
        pass
    
    shopping_cart = Cart.objects.get(pk=shopping_cart_id)
    product = Product.objects.get(pk=product_id)
    shopping_cart.add_product(product)
    #TODO: Class based views. Really.
    