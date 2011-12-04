from shop.models.ordermodel import OrderExtraInfo, Order
from django.test.testcases import TestCase
from django.contrib.auth.models import User
from shop.tests.util import Mock
from shop.shop_api import ShopAPI
from decimal import Decimal


class ShopApiTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test",
            email="test@example.com")

        self.request = Mock()
        setattr(self.request, 'user', None)

        self.order = Order()
        self.order.order_subtotal = Decimal('10')
        self.order.order_total = Decimal('10')
        self.order.shipping_cost = Decimal('0')

        self.order.shipping_address_text = 'shipping address example'
        self.order.billing_address_text = 'billing address example'

        self.order = Order.objects.create()

    def test_add_extra_info(self):
        api = ShopAPI()
        api.add_extra_info(self.order, 'test')
        # Assert that an ExtraOrderInfo item was created
        oei = OrderExtraInfo.objects.get(order=self.order)
        self.assertEqual(oei.text, 'test')

    def test_is_order_payed(self):
        api = ShopAPI()
        res = api.is_order_payed(self.order)
        self.assertEqual(res, False)

    def test_is_order_complete(self):
        api = ShopAPI()
        res = api.is_order_completed(self.order)
        self.assertEqual(res, False)

    def test_get_order_total(self):
        api = ShopAPI()
        res = api.get_order_total(self.order)
        self.assertEqual(res, Decimal('0'))

    def test_get_order_subtotal(self):
        api = ShopAPI()
        res = api.get_order_subtotal(self.order)
        self.assertEqual(res, Decimal('0'))

    def test_get_order_short_name(self):
        api = ShopAPI()
        res = api.get_order_short_name(self.order)
        self.assertEqual(res, '1-0.00')

    def test_get_order_unique_id(self):
        api = ShopAPI()
        res = api.get_order_unique_id(self.order)
        self.assertEqual(res, 1)

    def test_get_order_for_id(self):
        api = ShopAPI()
        res = api.get_order_for_id(1)
        self.assertEqual(res, self.order)
