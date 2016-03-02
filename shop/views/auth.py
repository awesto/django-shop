# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_auth.views import LoginView as OriginalLoginView
from shop.models.cart import CartModel
from shop.rest.auth import PasswordResetSerializer, PasswordResetConfirmSerializer


class AuthFormsView(GenericAPIView):
    """
    Generic view to handle authetication related forms such as user registration
    """
    serializer_class = None
    form_class = None

    def post(self, request, *args, **kwargs):
        if request.customer.is_visitor():
            errors = {NON_FIELD_ERRORS: _("Unable to proceed as guest without items in the cart.")}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        form = self.form_class(data=request.data, instance=request.customer)
        if form.is_valid():
            form.save(request=request)
            return Response(form.data, status=status.HTTP_200_OK)
        return Response(dict(form.errors), status=status.HTTP_400_BAD_REQUEST)


class LoginView(OriginalLoginView):
    def login(self):
        """
        Logs in as the given user, and moves the items from the current to the new cart.
        """
        try:
            anonymous_cart = CartModel.objects.get_from_request(self.request)
        except CartModel.DoesNotExist:
            anonymous_cart = None
        dead_user = None if self.request.user.is_anonymous() or self.request.customer.is_registered() else self.request.customer.user
        super(LoginView, self).login()  # this rotates the session_key
        authenticated_cart = CartModel.objects.get_from_request(self.request)
        if anonymous_cart:
            anonymous_cart.items.update(cart=authenticated_cart)
        if dead_user and dead_user.is_active is False:
            dead_user.delete()  # to keep the database clean


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
        request.user = AnonymousUser()
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
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
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
        data = {'uid': uidb64, 'token': token}
        serializer_class = self.get_serializer_class()
        password = 'x' * serializer_class._declared_fields['new_password1']._kwargs.get('min_length', 3)
        data.update(new_password1=password, new_password2=password)
        serializer = serializer_class(data=data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response({'validlink': False})
        return Response({'validlink': True, 'user_name': force_text(serializer.user)})

    def post(self, request, uidb64=None, token=None):
        data = dict(request.data, uid=uidb64, token=token)
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({"success": _("Password has been reset with the new password.")})
