from django.conf import settings
from shop.util.loader import load_class


PAYMENT_BACKEND_MODEL = getattr(settings, 'SHOP_PAYMENTBACKEND_MODEL',
    'shop.models.defaults.payment.PaymentBackend')
PaymentBackend = load_class(PAYMENT_BACKEND_MODEL, 'SHOP_PAYMENTBACKEND_MODEL')
