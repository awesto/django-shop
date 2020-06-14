from django.conf.urls import url
from shop.forms.auth import RegisterUserForm, ContinueAsGuestForm
from shop.views.auth import AuthFormsView, LoginView, LogoutView, PasswordChangeView, PasswordResetRequestView

urlpatterns = [
    url(r'^password/reset/?$', PasswordResetRequestView.as_view(),
        name='password-reset-request'),
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
