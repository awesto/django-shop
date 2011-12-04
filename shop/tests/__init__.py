# flake8: noqa
from api import ShopApiTestCase
from cart import CartTestCase
from cart_modifiers import (
    CartModifiersTestCase,
    TenPercentPerItemTaxModifierTestCase,
)
from order import (
    OrderConversionTestCase,
    OrderPaymentTestCase,
    OrderTestCase,
    OrderUtilTestCase,
)
from forms import (
    CartItemModelFormTestCase,
    GetCartItemFormsetTestCase,
)
from payment import PayOnDeliveryTestCase, GeneralPaymentBackendTestCase
from product import ProductTestCase, ProductStatisticsTestCase
from shipping import (
    FlatRateShippingTestCase,
    GeneralShippingBackendTestCase,
    ShippingApiTestCase,
)
from templatetags import ProductsTestCase
from util import (
    AddressUtilTestCase,
    CartUtilsTestCase,
    CurrencyFieldTestCase,
    LoaderTestCase,
)
from views import (
    CartDetailsViewTestCase,
    CartViewTestCase,
    OrderListViewTestCase,
    ProductDetailViewTestCase,
)
from views_checkout import (
    CheckoutCartToOrderTestCase,
    ShippingBillingViewOrderStuffTestCase,
    ShippingBillingViewTestCase,
    ThankYouViewTestCase,
)
