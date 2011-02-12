# -*- coding: utf-8 -*-
from shop.models.cartmodel import Cart

def get_or_create_cart(request):
    '''
    Let's inspect the request for session or for user, then either find a
    matching cart and return it or create a new one bound to the user (if one
    exists), or to the session.
    '''
    cart = None
    if request.user:
        # There is a logged in user
        cart = Cart.objects.filter(user=request.user) # a list
        if not cart: # if list is empty
            cart = Cart.objects.create(user=request.user)
        else:
            cart = cart[0] # Get the first one from the list
    else:
        session = getattr(request, 'session', None)
        if session != None :
            # There is a session
            cart_id = session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(pk=cart_id)
            else:
                cart = Cart.objects.create()
                session['cart_id'] = cart.id
            
    return cart