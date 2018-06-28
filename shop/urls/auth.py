# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from shop.forms.auth import RegisterUserForm, ContinueAsGuestForm
from shop.views.auth import AuthFormsView, LoginView, LogoutView, PasswordChangeView, PasswordResetView

urlpatterns = [
    url(r'^password/reset/?$', PasswordResetView.as_view(),
        name='password-reset'),
    url(r'^login/?$', LoginView.as_view(),
        name='login'),
    url(r'^register/?$', AuthFormsView.as_view(form_class=RegisterUserForm),
        name='register-user'),
    url(r'^continue/?$', AuthFormsView.as_view(form_class=ContinueAsGuestForm),
        name='continue-as-guest'),

    url(r'^logout/?$', LogoutView.as_view(),
        name='logout'),
    url(r'^password/change/?$', PasswordChangeView.as_view(),
        name='password-change'),
]
