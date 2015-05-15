# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from rest_auth.views import Login, PasswordChange
from shop.forms.auth import RegisterUserForm
from shop.views.auth import AuthFormsView, LogoutView, PasswordResetView

urlpatterns = patterns(
    '',
    # URLs that do not require a session or valid token
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='password-reset'),
    url(r'^login/$', Login.as_view(),
        name='login'),
    url(r'^register/$', AuthFormsView.as_view(form_class=RegisterUserForm),
        name='register-user'),

    # URLs that require a user to be logged in with a valid session / token.
    url(r'^logout/$', LogoutView.as_view(),
        name='logout'),
    url(r'^password/change/$', PasswordChange.as_view(),
        name='password-change'),
)
