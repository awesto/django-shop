import pytest
import pytz
import re
from datetime import timedelta
from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.urls import reverse
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
    expires = datetime.strptime(session_cookie['expires'], '%a, %d %b %Y %H:%M:%S GMT')
    expires = expires.replace(tzinfo=tz_gmt)
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
    payload = response.json()
    if DJANGO_VERSION < (3,):
        assert payload == {'password_change_form': {'new_password2': ["The two password fields didn't match."]}}
    else:
        assert payload == {'password_change_form': {'new_password2': ["The two password fields didn’t match."]}}


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
    assert len(mail.outbox) == 1
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


@pytest.mark.django_db
def test_register_user_with_password(api_client):
    """
    Test if a new user can register himself providing his own new password.
    """
    from testshop.models import Customer
    register_user_url = reverse('shop:register-user')
    data = {
        'form_data': {
            'email': 'newby@example.com',
            'password1': 'secret',
            'password2': 'secret',
            'preset_password': False,
        }
    }
    response = api_client.post(register_user_url, data, format='json')
    assert response.status_code == 200
    assert response.json() == {'register_user_form': {'success_message': 'Successfully registered yourself.'}}
    customer = Customer.objects.get(user__email='newby@example.com')
    assert customer is not None


@pytest.mark.django_db
def test_register_user_generate_password(settings, api_client):
    """
    Test if a new user can register himself and django-SHOP send a generated password by email.
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    from testshop.models import Customer
    register_user_url = reverse('shop:register-user')
    data = {
        'form_data': {
            'email': 'newby@example.com',
            'password1': '',
            'password2': '',
            'preset_password': True,
        }
    }
    response = api_client.post(register_user_url, data, format='json')
    assert response.status_code == 200
    assert response.json() == {'register_user_form': {'success_message': 'Successfully registered yourself.'}}
    customer = Customer.objects.get(user__email='newby@example.com')
    assert customer is not None
    body_begin = "You're receiving this e-mail because you or someone else has requested an auto-generated password"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].body.startswith(body_begin)
    matches = re.search('please use username newby@example.com with password ([0-9A-Za-z]+)', mail.outbox[0].body)
    assert matches
    password = matches.group(1)
    assert api_client.login(username=customer.email, password=password) is True


@pytest.mark.django_db
def test_register_user_fail(registered_customer, api_client):
    """
    Test if a new user cannot register himself, if that user already exists.
    """
    register_user_url = reverse('shop:register-user')
    data = {
        'form_data': {
            'email': registered_customer.email,
            'password1': '',
            'password2': '',
            'preset_password': True,
        }
    }
    response = api_client.post(register_user_url, data, format='json')
    assert response.status_code == 422
    assert response.json() == {
        'register_user_form': {
            '__all__': ["A customer with the e-mail address 'admin@example.com' already exists.\nIf you have used this address previously, try to reset the password."]
        }
    }
