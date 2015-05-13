# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
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
    Password reset e-mail link points onto this view, which when invoked by a GET request renderes
    a HTML page containing a password reset form. This form then can be used to reset the user's
    password using a RESTful POST request.

    Since the URL for this view is part in the email's body text, expose it to the URL patterns as:

    ```
    url(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    ```

    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)
    template_name = 'shop/auth/password-reset-confirm.html'
    token_generator = default_token_generator

    def get(self, request, uidb64=None, token=None):
        user = self.get_user_from_tokens(uidb64, token)
        if user is None:
            return Response({'validlink': False})
        return Response({'validlink': True, 'user_name': force_text(user)})

    def post(self, request, uidb64=None, token=None):
        serializer = self.get_serializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({"success": "Password has been reset with the new password."})

    def get_user_from_tokens(self, uidb64, token):
        """
        If URL tokens are valid, return the corresponding user. Otherwise return None.
        """
        UserModel = get_user_model()
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and self.token_generator.check_token(user, token):
            return user
