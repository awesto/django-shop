# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def handle_customer_login(sender, **kwargs):
    request = kwargs['request']
    user = kwargs['user']
    if hasattr(user, 'customer'):
        request.customer.delete()
        request.customer = user.customer
    else:
        request.customer.user = user
        request.customer.save()
