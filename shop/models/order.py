# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import with_metaclass
from django.conf import settings
from django.db import models, transaction
from django.db.models.aggregates import Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.module_loading import import_by_path
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from jsonfield.fields import JSONField
from django_fsm import FSMField, transition
from cms.models import Page
from shop import settings as shop_settings
from shop.money.fields import MoneyField
from . import deferred


class OrderManager(models.Manager):
    @transaction.commit_on_success
    def create_from_cart(self, cart, request):
        """
        This creates a new Order object with all its OrderItems using the current Cart object
        with its CartItems.
        """
        cart.update(request)
        order = self.model(user=cart.user)
        order.save()
        for cart_item in cart.items.all():
            cart_item.update(request)
            order_item = OrderItemModel(order=order)
            order_item.populate_from_cart_item(cart_item, request)
            order_item.save()
        order.populate_from_cart(cart, request)
        order.save()
        cart.delete()
        return order


class WorkflowMixinMetaclass(deferred.ForeignKeyBuilder):
    """
    Add configured Workflow mixin classes to `OrderModel` and `OrderPayment` to customize all kinds
    of state transitions in a pluggable manner.
    """
    def __new__(cls, name, bases, attrs):
        if 'BaseOrder' in (b.__name__ for b in bases):
            bases = tuple(import_by_path(mc) for mc in shop_settings.ORDER_WORKFLOWS) + bases
        elif name == 'OrderPayment':
            bases = tuple(import_by_path(mc) for mc in shop_settings.PAYMENT_WORKFLOWS) + bases
        Model = super(WorkflowMixinMetaclass, cls).__new__(cls, name, bases, attrs)
        return Model


@python_2_unicode_compatible
class BaseOrder(with_metaclass(WorkflowMixinMetaclass, models.Model)):
    """
    An Order is the "in process" counterpart of the shopping cart, which freezes the state of the
    cart on the moment of purchase. It also holds stuff like the shipping and billing addresses,
    and keeps all the additional entities, as determined by the cart modifiers.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Customer"))
    status = FSMField(default='new', protected=True, verbose_name=_("Status"))
    subtotal = MoneyField(verbose_name=_("Subtotal"))
    total = MoneyField(verbose_name=_("Total"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    extra_rows = JSONField(null=True, blank=True,
        verbose_name=_("Extra rows for this order"))
    objects = OrderManager()

    class Meta:
        abstract = True
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __init__(self, *args, **kwargs):
        super(BaseOrder, self).__init__(*args, **kwargs)
        # find the page used for Order list views
        try:
            self.order_page = Page.objects.public().get(reverse_id='shop-order')
        except Page.DoesNotExist:
            self.order_page = Page.objects.public().filter(application_urls='OrderApp').first()

    def __str__(self):
        return _("Order ID: {}").format(self.pk)

    def get_absolute_url(self):
        return urljoin(self.order_page.get_absolute_url(), str(self.id))

    @transition(field=status, source='new', target='created')
    def populate_from_cart(self, cart, request):
        """
        Populate the order object with the fields from the given cart. Override this method,
        in case a customized cart has some fields which have to be transfered to the cart.
        """
        self.subtotal = cart.subtotal
        self.total = cart.total
        self.extra_rows = [(modifier, extra_row.data) for modifier, extra_row in cart.extra_rows.items()]

    def get_amount_paid(self):
        """
        The amount paid is the sum of related orderpayments
        """
        amount = self.orderpayment_set.aggregate(amount=Sum('amount'))['amount']
        if amount is None:
            amount = type(self.total)(0)
        return amount

    @property
    def short_name(self):
        """
        A short name for the order, to be displayed on the payment processor's
        website. Should be human-readable, as much as possible.
        """
        return "%s-%s" % (self.pk, self.order_total)

OrderModel = deferred.MaterializedModel(BaseOrder)


class OrderPayment(with_metaclass(WorkflowMixinMetaclass, models.Model)):
    """
    A class to hold basic payment information. Backends should define their own
    more complex payment types should they need to store more informtion
    """
    order = deferred.ForeignKey(BaseOrder, verbose_name=_("Order"))
    status = FSMField(default='new', protected=True, verbose_name=_("Status"))
    amount = MoneyField(verbose_name=_("Amount paid"),
        help_text=_("How much was paid with this particular transfer."))
    transaction_id = models.CharField(max_length=255, verbose_name=_("Transaction ID"),
        help_text=_("The transaction processor's reference"))
    payment_method = models.CharField(max_length=255, verbose_name=_("Payment method"),
        help_text=_("The payment backend used to process the purchase"))

    class Meta:
        verbose_name = _("Order payment")
        verbose_name_plural = _("Order payments")


class BaseOrderItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    An item for an order.
    """
    order = deferred.ForeignKey(BaseOrder, related_name='items', verbose_name=_("Order"))
    product_identifier = models.CharField(max_length=255, verbose_name=_("Product identifier"),
        help_text=_("Product identifier at the moment of purchase."))
    product_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Product name"),
        help_text=_("Product name at the moment of purchase."))
    product = deferred.ForeignKey('BaseProduct', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("Product"))
    unit_price = MoneyField(verbose_name=_("Unit price"),
        help_text=_("Products unit price at the moment of purchase."))
    line_total = MoneyField(verbose_name=_("Line Total"))
    quantity = models.IntegerField(verbose_name=_("Ordered quantity"))
    extra_rows = JSONField(null=True, blank=True,
        verbose_name=_("Extra rows for this order item"))

    class Meta:
        abstract = True
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")

    def populate_from_cart_item(self, cart_item, request):
        self.product = cart_item.product
        self.product_name = cart_item.product.name  # store the name on the moment of purchase, in case it changes
        self.product_identifier = cart_item.product.identifier
        self.unit_price = cart_item.product.get_price(request)
        self.line_total = cart_item.line_total
        self.quantity = cart_item.quantity
        self.extra_rows = [(modifier, extra_row.data) for modifier, extra_row in cart_item.extra_rows.items()]

OrderItemModel = deferred.MaterializedModel(BaseOrderItem)
