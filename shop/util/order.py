#-*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from shop.models.ordermodel import Order, OrderItem
from shop.util.cart import get_or_create_cart


def get_order_from_request(request):
    """
    Returns the currently processing Order from a request (switches between
    user or session mode) if any.
    """
    order = None
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged in user
        orders = Order.objects.filter(user=request.user)
        orders = orders.filter(status__lt=Order.COMPLETED)
        orders = orders.order_by('-created')
        if len(orders) >= 1:  # The queryset returns a list
            order = orders[0]
        else:
            # There is a logged in user but he has no pending order
            order = None
    else:
        session = getattr(request, 'session', None)
        if session != None:
            # There is a session
            order_id = session.get('order_id')
            if order_id:
                order = Order.objects.get(pk=order_id)
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
        request.session['order_id'] = order.id

def copy_order_item_to_cart(request, order, item_id):
    """
    Copy the item with the given id back to the cart. The item must be part
    of the given order, otherwise it is not copied. This is to assure the privacy
    of orders not belonging to the calling user.
    """
    item = OrderItem.objects.filter(order=order, id=item_id)
    if item != None:
        item = item[0]
        cart = get_or_create_cart(request)
        cart.save()
        cart.add_product(item.product, item.quantity, item.variation)
        cart.update()
