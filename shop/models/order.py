# -*- coding: utf-8 -*-
from six import with_metaclass
from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.db import models, transaction
from django.db.models.aggregates import Sum
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from shop.util.fields import CurrencyField
from shop.order_signals import processing
from . import deferred


class OrderManager(models.Manager):
    def get_latest_for_user(self, user):
        """
        Returns the last Order (from a time perspective) a given user has
        placed.
        """
        if user and not isinstance(user, AnonymousUser):
            return self.filter(user=user).order_by('-modified')[0]
        else:
            return None

    def get_unconfirmed_for_cart(self, cart):
        return self.filter(cart_pk=cart.pk, status__lt=self.model.CONFIRMED)

    def remove_old_orders(self, cart):
        """
        Removes all old unconfirmed order objects.
        """
        old_orders = self.get_unconfirmed_for_cart(cart)
        old_orders.delete()

    def create_order_object(self, cart, request):
        """
        Create an empty order object and fill it with the given cart data.
        """
        order = self.model()
        order.cart_pk = cart.pk
        order.user = cart.user
        order.status = self.model.PROCESSING  # Processing
        order.order_subtotal = cart.subtotal_price
        order.order_total = cart.total_price
        return order

    @transaction.commit_on_success
    def create_from_cart(self, cart, request):
        """
        This creates a new Order object (and all the rest) from a passed Cart
        object.

        Specifically, it creates an Order with corresponding OrderItems and
        eventually corresponding ExtraPriceFields

        This will only actually commit the transaction once the function exits
        to minimize useless database access.

        The `state` parameter is further passed to process_cart_item,
        process_cart, and post_process_cart, so it can be used as a way to
        store per-request arbitrary information.

        Emits the ``processing`` signal.
        """
        from .cart import BaseCartItem
        CartItem = getattr(BaseCartItem, 'MaterializedModel')
        OrderItem = getattr(BaseOrderItem, 'MaterializedModel')

        # First, let's remove old orders
        self.remove_old_orders(cart)

        # Create an empty order object
        order = self.create_order_object(cart, request)
        order.save()

        # Let's serialize all the extra price arguments in DB
        for field in cart.extra_price_fields:
            eoi = ExtraOrderPriceField()
            eoi.order = order
            eoi.label = unicode(field[0])
            eoi.value = field[1]
            if len(field) == 3:
                eoi.data = field[2]
            eoi.save()

        # There, now move on to the order items.
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            item.update(request)
            order_item = OrderItem()
            order_item.order = order
            order_item.product_reference = item.product.get_product_reference()
            order_item.product_name = item.product.get_name()
            order_item.product = item.product
            order_item.unit_price = item.product.get_price()
            order_item.quantity = item.quantity
            order_item.line_total = item.line_total
            order_item.line_subtotal = item.line_subtotal
            order_item.save()
            # For each order item, we save the extra_price_fields to DB
            for field in item.extra_price_fields:
                eoi = ExtraOrderItemPriceField()
                eoi.order_item = order_item
                # Force unicode, in case it has àö...
                eoi.label = unicode(field[0])
                eoi.value = field[1]
                if len(field) == 3:
                    eoi.data = field[2]
                eoi.save()

        processing.send(self.model, order=order, cart=cart)
        return order


@python_2_unicode_compatible
class BaseOrder(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    A model representing an Order.

    An order is the "in process" counterpart of the shopping cart, which holds
    stuff like the shipping and billing addresses (copied from the User
    profile) when the Order is first created), list of items, and holds stuff
    like the status, shipping costs, taxes, etc.
    """

    PROCESSING = 10  # New order, addresses and shipping/payment methods chosen (user is in the shipping backend)
    CONFIRMING = 20  # The order is pending confirmation (user is on the confirm view)
    CONFIRMED = 30  # The order was confirmed (user is in the payment backend)
    COMPLETED = 40  # Payment backend successfully completed
    SHIPPED = 50  # The order was shipped to client
    CANCELED = 60  # The order was canceled
    CANCELLED = CANCELED  # DEPRECATED SPELLING

    PAYMENT = 30  # DEPRECATED!

    STATUS_CODES = (
        (PROCESSING, _('Processing')),
        (CONFIRMING, _('Confirming')),
        (CONFIRMED, _('Confirmed')),
        (COMPLETED, _('Completed')),
        (SHIPPED, _('Shipped')),
        (CANCELED, _('Canceled')),
    )

    # If the user is null, the order was created with a session
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
            verbose_name=_("User"))
    status = models.IntegerField(choices=STATUS_CODES, default=PROCESSING,
            verbose_name=_("Status"))
    order_subtotal = CurrencyField(verbose_name=_("Order subtotal"))
    order_total = CurrencyField(verbose_name=_("Order Total"))
    shipping_address_text = models.TextField(_('Shipping address'), blank=True,
        null=True)
    billing_address_text = models.TextField(_('Billing address'), blank=True,
        null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    cart_pk = models.PositiveIntegerField(_('Cart primary key'), blank=True, null=True)

    # override manager
    objects = OrderManager()

    class Meta:
        abstract = True
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return _("Order ID: {id}").format(id=self.pk)

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def is_paid(self):
        """Has this order been integrally paid for?"""
        return self.amount_paid >= self.order_total
    is_payed = is_paid  # TODO: remove deprecated spelling

    def is_completed(self):
        return self.status == self.COMPLETED

    def get_status_name(self):
        return dict(self.STATUS_CODES)[self.status]

    @property
    def amount_paid(self):
        """
        The amount paid is the sum of related orderpayments
        """
        sum_ = OrderPayment.objects.filter(order=self).aggregate(
                sum=Sum('amount'))
        result = sum_.get('sum')
        if result is None:
            result = Decimal(0)
        return result
    amount_payed = amount_paid  # deprecated spelling

    @property
    def shipping_costs(self):
        sum_ = Decimal('0.0')
        cost_list = ExtraOrderPriceField.objects.filter(order=self).filter(
                is_shipping=True)
        for cost in cost_list:
            sum_ += cost.value
        return sum_

    @property
    def short_name(self):
        """
        A short name for the order, to be displayed on the payment processor's
        website. Should be human-readable, as much as possible.
        """
        return "%s-%s" % (self.pk, self.order_total)

    def set_billing_address(self, billing_address):
        """
        Process billing_address trying to get as_text method from address
        and copying.
        You can override this method to process address more granulary
        e.g. you can copy address instance and save FK to it in your order
        class.
        """
        if hasattr(billing_address, 'as_text') and callable(billing_address.as_text):
            self.billing_address_text = billing_address.as_text()
            self.save()

    def set_shipping_address(self, shipping_address):
        """
        Process shipping_address trying to get as_text method from address
        and copying.
        You can override this method to process address more granulary
        e.g. you can copy address instance and save FK to it in your order
        class.
        """
        if hasattr(shipping_address, 'as_text') and callable(shipping_address.as_text):
            self.shipping_address_text = shipping_address.as_text()
            self.save()


class OrderPayment(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    A class to hold basic payment information. Backends should define their own
    more complex payment types should they need to store more informtion
    """
    class Meta:
        app_label = 'shop'
        verbose_name = _('Order payment')
        verbose_name_plural = _('Order payments')

    order = deferred.ForeignKey(BaseOrder, verbose_name=_('Order'))
    # How much was paid with this particular transfer
    amount = CurrencyField(verbose_name=_('Amount'))
    transaction_id = models.CharField(max_length=255, verbose_name=_('Transaction ID'),
            help_text=_("The transaction processor's reference"))
    payment_method = models.CharField(max_length=255, verbose_name=_('Payment method'),
            help_text=_("The payment backend used to process the purchase"))


class BaseExtraOrderRow(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    This will make Cart-provided extra row fields persistent, since we want to "snapshot" their
    statuses at the time when the order was made.
    """
    class Meta:
        abstract = True
        verbose_name = _("Extra order row")
        verbose_name_plural = _("Extra order rows")

    order = deferred.ForeignKey(BaseOrder, verbose_name=_('Order'))
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    value = CurrencyField(verbose_name=_('Amount'))


class OrderAnnotation(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    A holder for extra textual information to attach to this order.
    """
    class Meta:
        app_label = 'shop'
        verbose_name = _("Order annotation")
        verbose_name_plural = _("Order annotations")

    order = deferred.ForeignKey(BaseOrder, related_name="extra_info", verbose_name=_("Order"))
    text = models.TextField(verbose_name=_("Annotation text"), blank=True)


class BaseOrderItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    An item for an order.
    """
    class Meta:
        abstract = True
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")

    order = deferred.ForeignKey(BaseOrder, related_name='items', verbose_name=_("Order"))
    product_code = models.CharField(max_length=255, verbose_name=_("Product reference"))
    product_name = models.CharField(max_length=255, null=True, blank=True,
        verbose_name=_("Product name"))
    product = models.ForeignKey('Product', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("Product"))
    unit_price = CurrencyField(verbose_name=_("Unit price"))
    quantity = models.IntegerField(verbose_name=_("Quantity"))
    line_subtotal = CurrencyField(verbose_name=_("Line subtotal"))
    line_total = CurrencyField(verbose_name=_("Line total"))

    def save(self, *args, **kwargs):
        if not self.product_name and self.product:
            self.product_name = self.product.get_name()
        super(BaseOrderItem, self).save(*args, **kwargs)


class BaseExtraOrderItemRow(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    class Meta:
        abstract = True
        verbose_name = _('Extra order item price field')
        verbose_name_plural = _('Extra order item price fields')

    order_item = deferred.ForeignKey(BaseOrderItem, verbose_name=_("Order item"))
    label = models.CharField(max_length=255, verbose_name=_("Label"))
    amount = CurrencyField(verbose_name=_("Amount"))
