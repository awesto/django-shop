from cartmodel import *
from ordermodel import *
from productmodel import *
from shop.order_signals import *
from shop.util.loader import load_class

"""
Load the class specified by the user as the Address Model.
"""
AddressModel = load_class(getattr(settings, 'SHOP_ADDRESS_MODEL', 'shop.addressmodel.models.Address'))
