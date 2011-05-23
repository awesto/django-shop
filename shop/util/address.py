#-*- coding: utf-8 -*-
from django.conf import settings
from shop.util.loader import load_class

"""
Load the class specified by the user as the Address Model.
"""
AddressModel = load_class(settings.SHOP_ADDRESS_MODEL or 'shop.clientmodel.models.Address')

#===============================================================================
# Addresses handling
#===============================================================================

def get_shipping_address_from_request(request):
    """
    Get the shipping address from the request. This abstracts the fact that users
    can be either registered (and thus, logged in), or only session-based guests
    """
    # TODO: Implement

def get_billing_address_from_request(request):
    """
    Get the billing address from the request. This abstracts the fact that users
    can be either registered (and thus, logged in), or only session-based guests
    """
    # TODO: Implement
    
def assign_address_to_request(request, address, shipping=True):
    """
    Sets the passed address as either the shipping or the billing address for the
    passed request.
    This abstracts the difference between logged-in users and session-based guests.
    
    The `shipping` parameter controls whether the address is a shipping address 
    (default) or a billing address.
    """
    # TODO: Implement
