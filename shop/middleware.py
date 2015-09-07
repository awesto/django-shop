# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.functional import SimpleLazyObject

def get_customer(request, force=False):
    from shop.models.customer import CustomerModel as Customer
    if force or not hasattr(request, '_cached_customer'):
        request._cached_customer = Customer.objects.get_customer(request)
    return request._cached_customer

class CustomerMiddleware(object):
    def process_request(self, request):
        request.customer = SimpleLazyObject(lambda: get_customer(request))

