import binascii
from os import urandom
from urllib.parse import urljoin

from django.db import models
from django.utils import timezone
# from django.utils.translation import gettext_lazy as _, pgettext_lazy
from shop.shopmodels import order

from shop.shopmodels.order import BaseOrderItem
from django.db.models import PositiveIntegerField, BooleanField
# from django.utils.translation import gettext_lazy as _


class Order(order.BaseOrder):
    """Default materialized model for Order"""
    # number = models.PositiveIntegerField(
    #     _("Order Number"),
    #     null=True,
    #     default=None,
    #     unique=True,
    # )
    #
    # shipping_address_text = models.TextField(
    #     _("Shipping Address"),
    #     blank=True,
    #     null=True,
    #     help_text=_("Shipping address at the moment of purchase."),
    # )
    #
    # billing_address_text = models.TextField(
    #     _("Billing Address"),
    #     blank=True,
    #     null=True,
    #     help_text=_("Billing address at the moment of purchase."),
    # )
    #
    # token = models.CharField(
    #     _("Token"),
    #     max_length=40,
    #     editable=False,
    #     null=True,
    #     help_text=_("Secret key to verify ownership on detail view without requiring authentication."),
    # )
    #
    # class Meta:
    #     verbose_name = pgettext_lazy('order_models', "Order")
    #     verbose_name_plural = pgettext_lazy('order_models', "Orders")

    number = models.PositiveIntegerField(
        null=True,
        default=None,
        unique=True,
    )

    shipping_address_text = models.TextField(
        blank=True,
        null=True,
    )

    billing_address_text = models.TextField(
        blank=True,
        null=True,
    )

    token = models.CharField(
        max_length=40,
        editable=False,
        null=True,
    )

    class Meta:
        pass

    def get_or_assign_number(self):
        """
        Set a unique number to identify this Order object. The first 4 digits represent the
        current year. The last five digits represent a zero-padded incremental counter.
        """
        if self.number is None:
            epoch = timezone.now()
            epoch = epoch.replace(epoch.year, 1, 1, 0, 0, 0, 0)
            aggr = Order.objects.filter(number__isnull=False, created_at__gt=epoch).aggregate(models.Max('number'))
            try:
                epoc_number = int(str(aggr['number__max'])[4:]) + 1
                self.number = int('{0}{1:05d}'.format(epoch.year, epoc_number))
            except (KeyError, ValueError):
                # the first order this year
                self.number = int('{0}00001'.format(epoch.year))
        return self.get_number()

    def get_number(self):
        number = str(self.number)
        return '{}-{}'.format(number[:4], number[4:])

    @classmethod
    def resolve_number(cls, number):
        bits = number.split('-')
        return dict(number=''.join(bits))

    def assign_secret(self):
        self.token = binascii.hexlify(urandom(20)).decode()
        return self.token

    @property
    def secret(self):
        return self.token

    def get_absolute_url(self):
        url = super().get_absolute_url()
        if self.token:
            if not url.endswith('/'):
                url += '/'
            url = urljoin(url, self.token)
        return url

    def populate_from_cart(self, cart, request):
        self.shipping_address_text = cart.shipping_address.as_text() if cart.shipping_address else ''
        self.billing_address_text = cart.billing_address.as_text() if cart.billing_address else ''

        # in case one of the addresses was None, the customer presumably intended the other one.
        if not self.shipping_address_text:
            self.shipping_address_text = self.billing_address_text
        if not self.billing_address_text:
            self.billing_address_text = self.shipping_address_text
        super().populate_from_cart(cart, request)


class OrderPayment(models.Model):
    """
    A model to hold received payments for a given order.
    """
    # order = deferred.ForeignKey(
    #     BaseOrder,
    #     on_delete=models.CASCADE,
    #     verbose_name=_("Order"),
    # )
    #
    # amount = MoneyField(
    #     _("Amount paid"),
    #     help_text=_("How much was paid with this particular transfer."),
    # )
    #
    # transaction_id = models.CharField(
    #     _("Transaction ID"),
    #     max_length=255,
    #     help_text=_("The transaction processor's reference"),
    # )
    #
    # created_at = models.DateTimeField(
    #     _("Received at"),
    #     auto_now_add=True,
    # )
    #
    # payment_method = models.CharField(
    #     _("Payment method"),
    #     max_length=50,
    #     help_text=_("The payment backend used to process the purchase"),
    # )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
    transaction_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)

    class Meta:
        # verbose_name = pgettext_lazy('order_models', "Order payment")
        # verbose_name_plural = pgettext_lazy('order_models', "Order payments")
        pass

    def __str__(self):
        # return _("Payment ID: {}").format(self.id)
        return "Payment ID: {}".format(self.id)


class OrderItem(BaseOrderItem):
    """Default materialized model for OrderItem"""
    # quantity = PositiveIntegerField(_("Ordered quantity"))
    quantity = PositiveIntegerField()
    canceled = BooleanField(default=False)

    class Meta:
        # verbose_name = pgettext_lazy('order_models', "Ordered Item")
        # verbose_name_plural = pgettext_lazy('order_models', "Ordered Items")
        pass
