# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from shop.models.cart import CartModel as Cart, CartItemModel as CartItem
from shop.models.customer import CustomerModel as Customer

@receiver(user_logged_in)
def handle_customer_login(sender, **kwargs):
    """
    If logged-in User already has a Customer, swap that one in and copy all
    cart items (don't copy whole cart, as logged-in user's cart might already
    contain items).
    Delete old customer (including cart).
    
    If logged-in User doesn't have a Customer yet, assign the current anonymous
    one.
    """
    request = kwargs['request']
    user = kwargs['user']
    old_customer = Customer.objects.get_customer(request, force_unauth=True)
    
    if hasattr(user, 'customer'):
        new_cart = request.customer.cart
        try:
            old_cart = old_customer.cart
            # is there a more sensible way than iterating?
            for item in old_cart.items.all():
                CartItem.objects.get_or_create(
                    cart=new_cart,
                    product=item.product,
                    quantity=item.quantity,
                    extra=item.extra
                )
            old_customer.delete()
        except Cart.DoesNotExist:
            pass
    #else:
    # anonymous Customer is assigned to existing User by CustomerManger, nothing to do here

