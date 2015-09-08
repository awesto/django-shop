# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from shop.models.cart import CartModel as Cart

@receiver(user_logged_in)
def handle_customer_login(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']
    current_cart = Cart.objects.get_from_request(request)
    if hasattr(user, 'customer'):
        request.customer.delete()
        request.customer = user.customer
    else:
        request.customer.user = user
        request.customer.save()
    current_cart.customer = request.customer
    current_cart.save()
