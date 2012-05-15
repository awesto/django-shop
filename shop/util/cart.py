# -*- coding: utf-8 -*-
from shop.models.cartmodel import Cart
from django.contrib.auth.models import AnonymousUser


def get_or_create_cart(request, save=False):
    """
    Return cart for current visitor.

    Let's inspect the request for user or session, then either find a
    matching cart and return it or build a new one.

    If ``save`` is True, cart object will be explicitely saved.
    """
    cart = None
    if not hasattr(request, '_cart'):
        if request.user and not isinstance(request.user, AnonymousUser):
            # There is a logged in user
            cart = Cart.objects.filter(user=request.user)  # a list
            if not cart:  # if list is empty
                cart = Cart(user=request.user)
            else:
                cart = cart[0]  # Get the first one from the list
        else:
            session = getattr(request, 'session', None)
            if session != None:
                # There is a session
                cart_id = session.get('cart_id')
                if cart_id:
                    try:
                        cart = Cart.objects.get(pk=cart_id)
                    except Cart.DoesNotExist:
                        cart = None
                if not cart:
                    cart = Cart()
        if save and not cart.pk:
            cart.save()
            request.session['cart_id'] = cart.id
        setattr(request, '_cart', cart)
    cart = getattr(request, '_cart')  # There we *must* have a cart
    return cart
