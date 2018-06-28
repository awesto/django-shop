# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_auth.views import LoginView as OriginalLoginView, PasswordChangeView as OriginalPasswordChangeView

from shop.models.cart import CartModel
from shop.models.customer import CustomerModel
from shop.rest.auth import PasswordResetSerializer, PasswordResetConfirmSerializer
from shop.signals import email_queued


class AuthFormsView(GenericAPIView):
    """
    Generic view to handle authetication related forms such as user registration
    """
    serializer_class = None
    form_class = None

    def post(self, request, *args, **kwargs):
        if request.customer.is_visitor():
            customer = CustomerModel.objects.get_or_create_from_request(request)
        else:
            customer = request.customer
        form_data = request.data.get(self.form_class.scope_prefix, {})
        form = self.form_class(data=form_data, instance=customer)
        if form.is_valid():
            form.save(request=request)
            response_data = {form.form_name: {
                'success_message': _("Successfully registered yourself."),
            }}
            return Response(response_data, status=status.HTTP_200_OK)
        errors = dict(form.errors)
        if 'email' in errors:
            errors.update({NON_FIELD_ERRORS: errors.pop('email')})
        return Response({form.form_name: errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginView(OriginalLoginView):
    def login(self):
        """
        Logs in as the given user, and moves the items from the current to the new cart.
        """
        try:
            anonymous_cart = CartModel.objects.get_from_request(self.request)
        except CartModel.DoesNotExist:
            anonymous_cart = None
        if self.request.customer.user.is_anonymous() or self.request.customer.is_registered():
            previous_user = None
        else:
            previous_user = self.request.customer.user
        super(LoginView, self).login()  # this rotates the session_key
        authenticated_cart = CartModel.objects.get_from_request(self.request)
        if anonymous_cart:
            # an anonymous customer logged in, now merge his current cart with a cart,
            # which previously might have been created under his account.
            authenticated_cart.merge_with(anonymous_cart)
        if previous_user and previous_user.is_active is False and previous_user != self.request.user:
            previous_user.delete()  # keep the database clean and remove this anonymous entity

    def post(self, request, *args, **kwargs):
        self.request = request
        form_data = request.data.get('form_data', {})
        self.serializer = self.get_serializer(data=form_data)
        if self.serializer.is_valid():
            self.login()
            return self.get_response()

        exc = ValidationError({'login_form': self.serializer.errors})
        response = self.handle_exception(exc)
        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response


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
        response_data = {'logout_form': {'success_message': _("Successfully logged out.")}}
        return Response(response_data)


class PasswordChangeView(OriginalPasswordChangeView):
    def post(self, request, *args, **kwargs):
        form_data = request.data.get('form_data', {})
        serializer = self.get_serializer(data=form_data)
        if serializer.is_valid():
            serializer.save()
            response_data = {'change_form': {
                'success_message': _("Password has been changed successfully."),
            }}
            return Response(response_data)
        return Response({'change_form': serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class PasswordResetView(GenericAPIView):
    """
    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        form_data = request.data.get('form_data', {})
        serializer = self.get_serializer(data=form_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # trigger async email queue
        email_queued()

        # Return the success message with OK HTTP status
        msg = _("Instructions on how to reset the password have been sent to '{email}'.")
        response_data = {'reset_form': {
            'success_message': msg.format(**serializer.data),
        }}
        return Response(response_data)


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
        password = get_user_model().objects.make_random_password()
        data.update(new_password1=password, new_password2=password)
        serializer = serializer_class(data=data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response({'validlink': False})
        return Response({
            'validlink': True,
            'user_name': force_text(serializer.user),
            'form_name': 'password_reset_form',
        })

    def post(self, request, uidb64=None, token=None):
        data = dict(request.data, uid=uidb64, token=token)
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({"success": _("Password has been reset with the new password.")})
