# djangoshop/checkout.py

class CheckoutSite(object):
    """ code copied from AdminSite """
    pass

def autodiscover():
    pass

# djangoshop/__init__.py

from djangoshop.checkout import CheckoutSite
checkoutsite = CheckoutSite()

# djangoshop/shipper_base.py

class ShipperBase(object)
    pass
    
# djangoshop/payment_base.py

class PaymentBase(object)
    pass

# app/djangoshop_shipper.py

from djangoshop.shipper_base import ShipperBase

class ShipmentClass(ShipperBase):
    pass
    
checkoutsite.register_shipment(ShipmentClass)

# app/djangoshop_payment.py

from djangoshop.payment_base import PaymentBase

class PaymentClass(PaymentBase):
    pass
    
checkoutsite.register_payment(PaymentClass)
