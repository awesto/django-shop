import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.cache import SessionStore
from shop.models.customer import VisitingCustomer
from testshop.models import Customer


@pytest.mark.django_db
def test_visiting_customer(rf, session):
    """
    Check that an anonymous user creates a visiting customer.
    """
    request = rf.get('/', follow=True)
    request.user = AnonymousUser()
    request.session = session
    customer = Customer.objects.get_from_request(request)
    customer.save()
    assert isinstance(customer, VisitingCustomer)
    assert str(customer) == 'Visitor'
    assert customer.is_anonymous is True
    assert customer.is_authenticated is False
    assert customer.is_recognized is False
    assert customer.is_guest is False
    assert customer.is_registered is False
    assert customer.is_visitor is True


@pytest.mark.django_db
def test_unrecognized_customer(rf, session):
    """
    Check that an anonymous user creates an unrecognized customer.
    """
    request = rf.get('/', follow=True)
    request.user = AnonymousUser()
    request.session = session
    customer = Customer.objects.get_or_create_from_request(request)
    assert isinstance(customer, Customer)
    assert customer.is_anonymous is True
    assert customer.is_authenticated is False
    assert customer.is_recognized is False
    assert customer.is_guest is False
    assert customer.is_registered is False
    assert customer.is_visitor is False


@pytest.mark.django_db
def test_unexpired_customer(rf, session):
    """
    Check that an anonymous user creates an unrecognized customer using the current session-key.
    """
    request = rf.get('/', follow=True)
    request.user = AnonymousUser()
    request.session = SessionStore()
    customer = Customer.objects.get_or_create_from_request(request)
    assert isinstance(customer, Customer)
    assert customer.is_anonymous is True
    assert customer.is_expired is False
    assert Customer.objects.decode_session_key(customer.user.username) == request.session.session_key
    customer.delete()
    with pytest.raises(Customer.DoesNotExist):
        Customer.objects.get(pk=customer.pk)
    with pytest.raises(get_user_model().DoesNotExist):
        get_user_model().objects.get(pk=customer.pk)


@pytest.mark.django_db
def test_authenticated_purchasing_user(user_factory, rf, session):
    """
    Check that an authenticated Django user creates a recognized django-SHOP customer.
    """
    user = user_factory()
    with pytest.raises(Customer.DoesNotExist):
        Customer.objects.get(pk=user.pk)
    request = rf.get('/', follow=True)
    request.user = user
    request.session = session
    customer = Customer.objects.get_or_create_from_request(request)
    assert isinstance(customer, Customer)
    assert customer.is_anonymous is False
    assert customer.is_authenticated is True
    assert customer.is_recognized is True
    assert customer.is_guest is False
    assert customer.is_registered is True
    assert customer.is_visitor is False


@pytest.mark.django_db
def test_authenticated_visiting_user(user_factory, rf, session):
    """
    Check that an authenticated user creates a recognized customer visiting the site.
    """
    user = user_factory()
    with pytest.raises(Customer.DoesNotExist):
        Customer.objects.get(pk=user.pk)
    request = rf.get('/', follow=True)
    request.user = user
    request.session = SessionStore()
    customer = Customer.objects.get_from_request(request)
    assert isinstance(customer, Customer)
    assert customer.is_authenticated is True
    assert customer.is_recognized is True
    assert customer.is_registered is True


@pytest.mark.django_db
def test_authenticated_visiting_customer(customer_factory, rf, session):
    """
    Check that an authenticated user creates a recognized customer visiting the site.
    """
    request = rf.get('/', follow=True)
    request.user = customer_factory().user
    request.session = session
    customer = Customer.objects.get_from_request(request)
    assert isinstance(customer, Customer)
    assert customer.pk == request.user.pk
    assert customer.is_authenticated is True
    assert customer.is_recognized is True
    assert customer.is_registered is True
