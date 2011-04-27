from cart import CartTestCase
from cart_modifiers import CartModifiersTestCase
from order import ( OrderConversionTestCase, OrderTestCase, OrderUtilTestCase,
    OrderPaymentTestCase )
from client import ClientTestCase
from payment import PayOnDeliveryTestCase, GeneralPaymentBackendTestCase
from util import CurrencyFieldTestCase, CartUtilsTestCase
from shipping import GeneralShippingBackendTestCase, ShippingApiTestCase
from product import ProductTestCase
from views import ( ProductDetailViewTestCase, CartDetailsViewTestCase,
        CartViewTestCase, OrderListViewTestCase, CheckoutViewTestCase )
