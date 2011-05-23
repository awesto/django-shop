#-*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from shop.util.loader import load_class
from django.core.exceptions import ObjectDoesNotExist

"""
Load the class specified by the user as the Address Model.
"""
AddressModel = load_class(getattr(settings,'SHOP_ADDRESS_MODEL', None) or 'shop.clientmodel.models.Address')

#===============================================================================
# Addresses handling
#===============================================================================

def get_shipping_address_from_request(request):
    """
    Get the shipping address from the request. This abstracts the fact that users
    can be either registered (and thus, logged in), or only session-based guests
    """
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged-in user here, but he might not have an address defined.
        try:
            shipping_address = request.user.shipping_address
        except (AttributeError, ObjectDoesNotExist):
            shipping_address = None
    else:
        # The client is a guest - let's use the session instead.
        session = getattr(request, 'session', None)
        shipping_address = None
        if session != None :
            # There is a session
            shipping_address_id = session.get('shipping_address_id')
            if shipping_address_id:
                shipping_address = AddressModel.objects.get(pk=shipping_address_id)
    return shipping_address

def get_billing_address_from_request(request):
    """
    Get the billing address from the request. This abstracts the fact that users
    can be either registered (and thus, logged in), or only session-based guests
    """
    if request.user and not isinstance(request.user, AnonymousUser):
        # There is a logged-in user here, but he might not have an address defined.
        try:
            billing_address = request.user.billing_address
        except (AttributeError, ObjectDoesNotExist):
            billing_address = None
    else:
        # The client is a guest - let's use the session instead.
        session = getattr(request, 'session', None)
        if session != None :
            # There is a session
            billing_address_id = session.get('billing_address_id')
            if billing_address_id:
                billing_address = AddressModel.objects.get(pk=billing_address_id)
    return billing_address
    
def assign_address_to_request(request, address, shipping=True):
    """
    Sets the passed address as either the shipping or the billing address for the
    passed request.
    This abstracts the difference between logged-in users and session-based guests.
    
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
        # The client is a guest - let's use the session instead.
        # There has to be a session. Otherwise it's fine to get an AttributeError
        if shipping:
            request.session['shipping_address_id'] = address.pk
        else:
            request.session['billing_address_id'] = address.pk