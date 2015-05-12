# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import logout
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from shop.middleware import get_user


class AuthFormsView(GenericAPIView):
    """
    Generic view to handle authetication related forms such as user registration
    """
    serializer_class = None
    form_class = None

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.DATA, instance=request.user)
        if form.is_valid():
            form.save(request=request)
            return Response(form.data, status=status.HTTP_200_OK)
        return Response(dict(form.errors), status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    """
    Calls Django logout method and delete the auth Token assigned to the current User object.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        logout(request)
        request.user = get_user(request, True)
        return Response({"success": _("Successfully logged out.")}, status=status.HTTP_200_OK)
