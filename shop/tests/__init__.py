from cart import CartTestCase
from cart_modifiers import ( CartModifiersTestCase,
        TenPercentPerItemTaxModifierTestCase )
from order import ( OrderConversionTestCase, OrderTestCase, OrderUtilTestCase,
    OrderPaymentTestCase )
#from client import ClientTestCase
from payment import PayOnDeliveryTestCase, GeneralPaymentBackendTestCase
from util import (CurrencyFieldTestCase, CartUtilsTestCase, LoaderTestCase, 
                  AddressUtilTestCase)
from shipping import GeneralShippingBackendTestCase, ShippingApiTestCase
from product import ProductTestCase, ProductStatisticsTestCase
from views import ( ProductDetailViewTestCase, CartDetailsViewTestCase,
        CartViewTestCase, OrderListViewTestCase, CheckoutViewTestCase )
