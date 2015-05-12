# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import logout
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_auth.app_settings import PasswordResetConfirmSerializer
from shop.rest.auth import PasswordResetSerializer
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
        return Response({'success': _("Successfully logged out.")}, status=status.HTTP_200_OK)


class PasswordResetView(GenericAPIView):
    """
    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.DATA
        serializer = self.get_serializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # Return the success message with OK HTTP status
        msg = _("Instructions on how to reset the password have been sent to '{email}'.")
        return Response(
            {'success': msg.format(**serializer.data)},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirm(GenericAPIView):

    """
    Password reset e-mail link is confirmed, therefore this resets the user's password.

    Accepts the following POST parameters: new_password1, new_password2
    Accepts the following Django URL arguments: token, uid
    Returns the success/fail message.
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({"success": "Password has been reset with the new password."})
