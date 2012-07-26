# -*- coding: utf-8 -*-
from shop.models.cartmodel import Cart
from django.contrib.auth.models import AnonymousUser

def get_cart_from_database(request):
    database_cart = Cart.objects.filter(user=request.user)
    if database_cart:
        database_cart = database_cart[0]
    else:
        database_cart = None
    return database_cart

def get_cart_from_session(request):
    session_cart = None
    session = getattr(request, 'session', None)
    if session != None:
        cart_id = session.get('cart_id')
        if cart_id:
            try:
                session_cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                session_cart = None
    return session_cart

def get_or_create_cart(request, save=False):
    """
    Return cart for current visitor.

    For a logged in user, try to get the cart from the database. If it's not there or it's empty,
    use the cart from the session.
    If the user is not logged in use the cart from the session.
    If there is no cart object in the database or session, create one.

    If ``save`` is True, cart object will be explicitly saved.
    """
    cart = None
    if not hasattr(request, '_cart'):
        is_logged_in = request.user and not isinstance(request.user, AnonymousUser)

        if is_logged_in:
            # if we are authenticated, the database cart has priority
            database_cart = get_cart_from_database(request)
            if database_cart:
                # let's use the database cart
                cart = database_cart
                if database_cart.total_quantity < 1:
                    # if the database cart is empty, check the session cart
                    session_cart = get_cart_from_session(request)
                    if session_cart and session_cart.total_quantity > 0:
                        # the session cart is not empty, let's use it instead
                        cart = session_cart
                        database_cart.delete() # delete the old, empty one
                        database_cart = None
                        cart.user = request.user # and save the user to the new one
                        cart.save()
            else:
                # no cart in database, let's use the session cart
                cart = get_cart_from_session(request)
                if cart.user != request.user:
                    # save the user reference to the cart
                    cart.user = request.user
                    cart.save()
        else:
            # not authenticated? cart might be in session
            cart = get_cart_from_session(request)

        if not cart:
            # in case it's our first visit and no cart was created yet
            if is_logged_in:
                cart = Cart.objects.create(user=request.user)
            else:
                cart = Cart.objects.create()

        if save and not cart.pk:
            cart.save()

        request.session['cart_id'] = cart.id
        setattr(request, '_cart', cart)

    cart = getattr(request, '_cart')  # There we *must* have a cart
    return cart
