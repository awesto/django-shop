#-*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from shop.models.ordermodel import Order


def get_orders_from_request(request):
    """
    Returns all the Orders created from the provided request.
    """
    orders = None
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged in user
        orders = Order.objects.filter(user=request.user)
        orders = orders.order_by('-created')
    else:
        session = getattr(request, 'session', None)
        if session is not None:
            # There is a session
            order_id = session.get('order_id')
            if order_id:
                orders = Order.objects.filter(pk=order_id)
    return orders


def get_order_from_request(request):
    """
    Returns the currently processing Order from a request (switches between
    user or session mode) if any.
    """
    orders = get_orders_from_request(request)
    if orders and len(orders) >= 1:
        order = orders[0]
    else:
        order = None
    return order


def add_order_to_request(request, order):
    """
    Checks that the order is linked to the current user or adds the order to
    the session should there be no logged in user.
    """
    if request.user and not isinstance(request.user, AnonymousUser):
        # We should check that the current user is indeed the request's user.
        if order.user != request.user:
            order.user = request.user
            order.save()
    else:
        # Add the order_id to the session There has to be a session. Otherwise
        # it's fine to get an AttributeError
        request.session['order_id'] = order.pk
