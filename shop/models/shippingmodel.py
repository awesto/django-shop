from django.conf import settings
from shop.util.loader import load_class


SHIPPING_BACKEND_MODEL = getattr(settings, 'SHOP_SHIPPINGBACKEND_MODEL',
    'shop.models.defaults.shipping.ShippingBackend')
ShippingBackend = load_class(SHIPPING_BACKEND_MODEL, 'SHOP_SHIPPINGBACKEND_MODEL')
