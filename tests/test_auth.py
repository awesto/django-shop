# -*- coding: utf-8
from __future__ import unicode_literals

import pytest
import pytz
import re
from datetime import timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import mail
from django.utils.timezone import datetime
from shop.serializers.auth import PasswordResetRequestSerializer
from shop.views.auth import PasswordResetConfirmView


@pytest.mark.django_db
def test_login_fail(api_client):
    login_url = reverse('shop:login')
    data = {
        'form_data': {
            'username': 'a',
            'password': 'b',
        }
    }
    response = api_client.post(login_url, data, format='json')
    assert response.status_code == 400
    assert response.json() == {'login_form': {'non_field_errors': ['Unable to log in with provided credentials.']}}
    assert response.cookies.get('sessionid') is None


@pytest.mark.django_db
def test_login_success(registered_customer, api_client):
    login_url = reverse('shop:login')
    data = {
        'form_data': {
            'username': registered_customer.email,
            'password': 'secret',
        }
    }
    response = api_client.post(login_url, data, format='json')
    assert response.status_code == 200
    assert len(response.json().get('key')) == 40
    session_cookie = response.cookies.get('sessionid')
    assert session_cookie['expires'] == ''
    assert session_cookie['max-age'] == ''


@pytest.mark.django_db
def test_login_presistent(registered_customer, api_client):
    login_url = reverse('shop:login')
    data = {
        'form_data': {
            'username': registered_customer.email,
            'password': 'secret',
            'stay_logged_in': True
        }
    }
    response = api_client.post(login_url, data, format='json')
    tz_gmt = pytz.timezone('GMT')
    shall_expire = datetime.now(tz=tz_gmt).replace(microsecond=0) + timedelta(seconds=settings.SESSION_COOKIE_AGE)
    assert response.status_code == 200
    session_cookie = response.cookies.get('sessionid')
    expires = datetime.strptime(session_cookie['expires'], '%a, %d-%b-%Y %H:%M:%S GMT').replace(tzinfo=tz_gmt)
    assert abs(expires - shall_expire) < timedelta(seconds=5)
    assert session_cookie['max-age'] == settings.SESSION_COOKIE_AGE


@pytest.mark.django_db
def test_logout(registered_customer, api_client):
    assert api_client.login(username=registered_customer.email, password='secret') is True
    logout_url = reverse('shop:logout')
    response = api_client.post(logout_url, {}, format='json')
    assert response.status_code == 200
    assert response.json() == {'logout_form': {'success_message': 'Successfully logged out.'}}


@pytest.mark.django_db
def test_change_password_fail(registered_customer, api_client):
    assert api_client.login(username=registered_customer.email, password='secret') is True
    change_url = reverse('shop:password-change')
    data = {
        'form_data': {
            'new_password1': 'secret1',
            'new_password2': 'secret2',
        }
    }
    response = api_client.post(change_url, data, format='json')
    assert response.status_code == 422
    assert response.json() == {'password_change_form': {'new_password2': ["The two password fields didn't match."]}}


@pytest.mark.django_db
def test_change_password_success(registered_customer, api_client):
    api_client.login(username=registered_customer.email, password='secret')
    change_url = reverse('shop:password-change')
    data = {
        'form_data': {
            'new_password1': 'secret1',
            'new_password2': 'secret1',
        }
    }
    response = api_client.post(change_url, data, format='json')
    assert response.status_code == 200
    assert response.json() == {'password_change_form': {'success_message': 'Password has been changed successfully.'}}
    api_client.logout()
    assert api_client.login(username=registered_customer.email, password='secret') is False
    assert api_client.login(username=registered_customer.email, password='secret1') is True


@pytest.mark.django_db
def test_password_reset(settings, registered_customer, api_client, api_rf):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    reset_request_url = reverse('shop:password-reset-request')
    data = {
        'form_data': {
            'email': registered_customer.email,
        }
    }
    response = api_client.post(reset_request_url, data, format='json')
    assert response.status_code == 200
    assert response.json() == {
        'password_reset_request_form': {
            'success_message': "Instructions on how to reset the password have been sent to 'admin@example.com'."
        }
    }
    body_begin = "You're receiving this email because you requested a password reset for your user\naccount 'admin@example.com' at example.com."
    assert mail.outbox[0].body.startswith(body_begin)
    matches = re.search(PasswordResetRequestSerializer.invalid_password_reset_confirm_url + r'([^/]+)/([0-9A-Za-z-]+)',
                        mail.outbox[0].body)
    assert matches
    request = api_rf.get('/pasword-reset-confirm')
    response = PasswordResetConfirmView.as_view()(request, uidb64=matches.group(1), token=matches.group(2))
    assert response.status_code == 200
    assert response.data == {'validlink': True, 'user_name': 'admin@example.com', 'form_name': 'password_reset_form'}
    request = api_rf.post('/pasword-reset-confirm/', {'form_data': '__invalid__'})
    response = PasswordResetConfirmView.as_view()(request, uidb64=matches.group(1), token=matches.group(2))
    assert response.status_code == 422
    assert response.data == {'password_reset_confirm_form': {'non_field_errors': ['Invalid POST data.']}}
    data = {
        'form_data': {
            'new_password1': 'secret1',
            'new_password2': 'secret1',
        }
    }
    request = api_rf.post('/pasword-reset-confirm/', data, format='json')
    response = PasswordResetConfirmView.as_view()(request, uidb64=matches.group(1), token=matches.group(2))
    assert response.status_code == 200
    assert response.data == {'password_reset_confirm_form': {'success_message': 'Password has been reset with the new password.'}}


def test_password_reset_fail(api_rf):
    request = api_rf.get('/pasword-reset-confirm')
    response = PasswordResetConfirmView.as_view()(request, uidb64='INV', token='alid')
    assert response.status_code == 200
    assert response.data == {'validlink': False}
    data = {
        'form_data': {
            'new_password1': 'secret1',
            'new_password2': 'secret1',
        }
    }
    request = api_rf.post('/pasword-reset-confirm', data, format='json')
    response = PasswordResetConfirmView.as_view()(request, uidb64='INV', token='alid')
    assert response.status_code == 422
    assert response.data == {'password_reset_confirm_form': {'uid': ['Invalid value']}}
