# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from shop.models.customer import CustomerModel


def get_customer(request, force=False):
    if force or not hasattr(request, '_cached_customer'):
        if isinstance(request.user, AnonymousUser):
            request._cached_customer = CustomerModel.objects.get_from_request(request)
        else:
            request._cached_customer = request.user.customer
    return request._cached_customer


class CustomerMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The djangoSHOP middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        assert hasattr(request, 'user'), "The djangoSHOP middleware requires an authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'."
        request.customer = SimpleLazyObject(lambda: get_customer(request))
