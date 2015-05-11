# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model


def get_user(request):
    from django.contrib.auth.models import AnonymousUser

    if not hasattr(request, '_cached_user'):
        request._cached_user = auth.get_user(request)
    if isinstance(request._cached_user, AnonymousUser):
        request._cached_user = get_user_model().objects.get_from_request(request)
    return request._cached_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.user = SimpleLazyObject(lambda: get_user(request))
