# flake8: noqa
from __future__ import absolute_import
from .cart import CartTestCase
from .cart_modifiers import (
    CartModifiersTestCase,
    TenPercentPerItemTaxModifierTestCase,
)
from .order import (
    OrderConversionTestCase,
    OrderPaymentTestCase,
    OrderTestCase,
    OrderUtilTestCase,
)
from .forms import (
    CartItemModelFormTestCase,
    GetCartItemFormsetTestCase,
)
from .payment import PayOnDeliveryTestCase, GeneralPaymentBackendTestCase
from .product import ProductTestCase, ProductStatisticsTestCase
from .shipping import (
    FlatRateShippingTestCase,
    GeneralShippingBackendTestCase,
)
from .templatetags import ProductsTestCase
from .util import (
    AddressUtilTestCase,
    CartUtilsTestCase,
    CurrencyFieldTestCase,
    LoaderTestCase,
    ModelImportTestCase,
    CircularImportTestCase,
)
from .views import (
    CartDetailsViewTestCase,
    CartViewTestCase,
    OrderListViewTestCase,
    ProductListViewTestCase,
    ProductDetailViewTestCase,
)
from .views_checkout import (
    CheckoutCartToOrderTestCase,
    ShippingBillingViewOrderStuffTestCase,
    ShippingBillingViewTestCase,
    ThankYouViewTestCase,
)
