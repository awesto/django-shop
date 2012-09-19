from django.conf import settings

from cartmodel import *  # NOQA
from ordermodel import *  # NOQA
from productmodel import *  # NOQA
from shop.order_signals import *  # NOQA
from shop.util.loader import load_class

# Load the class specified by the user as the Address Model.
ShippingAddressModel = load_class(getattr(settings, 'SHOP_SHIPPING_ADDRESS_MODEL',
    getattr(settings, 'SHOP_ADDRESS_MODEL',
    'shop.addressmodel.models.Address')))
BillingAddressModel = load_class(getattr(settings, 'SHOP_BILLING_ADDRESS_MODEL',
    getattr(settings, 'SHOP_ADDRESS_MODEL',
    'shop.addressmodel.models.Address')))
