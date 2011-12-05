#-*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from shop.models import AddressModel


#==============================================================================
# Addresses handling
#==============================================================================

def get_shipping_address_from_request(request):
    """
    Get the shipping address from the request. This abstracts the fact that
    users can be either registered (and thus, logged in), or only session-based
    guests
    """
    shipping_address = None
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged-in user here, but he might not have an address
        # defined.
        try:
            shipping_address = AddressModel.objects.get(
                user_shipping=request.user)
        except AddressModel.DoesNotExist:
            shipping_address = None
    else:
        # The client is a guest - let's use the session instead.
        session = getattr(request, 'session', None)
        shipping_address = None
        session_address_id = session.get('shipping_address_id')
        if session != None and session_address_id:
            shipping_address = AddressModel.objects.get(pk=session_address_id)
    return shipping_address


def get_billing_address_from_request(request):
    """
    Get the billing address from the request. This abstracts the fact that
    users can be either registered (and thus, logged in), or only session-based
    guests
    """
    billing_address = None
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged-in user here, but he might not have an address
        # defined.
        try:
            billing_address = AddressModel.objects.get(
                user_billing=request.user)
        except AddressModel.DoesNotExist:
            billing_address = None
    else:
        # The client is a guest - let's use the session instead.
        session = getattr(request, 'session', None)
        session_billing_id = session.get('billing_address_id')
        if session != None and session_billing_id:
            billing_address = AddressModel.objects.get(pk=session_billing_id)
    return billing_address


def assign_address_to_request(request, address, shipping=True):
    """
    Sets the passed address as either the shipping or the billing address for
    the passed request.  This abstracts the difference between logged-in users
    and session-based guests.

    The `shipping` parameter controls whether the address is a shipping address
    (default) or a billing address.
    """
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged-in user here.
        if shipping:
            address.user_shipping = request.user
            address.save()
        else:
            address.user_billing = request.user
            address.save()
    else:
        # The client is a guest - let's use the session instead.  There has to
        # be a session. Otherwise it's fine to get an AttributeError
        if shipping:
            request.session['shipping_address_id'] = address.pk
        else:
            request.session['billing_address_id'] = address.pk


def get_user_name_from_request(request):
    """
    Simple helper to return the username from the request, or '' if the user is
    AnonymousUser.
    """
    name = ''
    if request.user and not isinstance(request.user, AnonymousUser):
        name = request.user.get_full_name()  # TODO: Administrators!
    return name
