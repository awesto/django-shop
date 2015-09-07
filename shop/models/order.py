# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import with_metaclass
from decimal import Decimal, ROUND_UP
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.db.models.aggregates import Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.module_loading import import_by_path
from django.utils.translation import ugettext_lazy as _, pgettext, get_language_from_request
from django.utils.six.moves.urllib.parse import urljoin
from jsonfield.fields import JSONField
from ipware.ip import get_ip
from django_fsm import FSMField, transition
from cms.models import Page
from shop import settings as shop_settings
from shop.money.fields import MoneyField, MoneyMaker
from . import deferred


class OrderManager(models.Manager):
    @transaction.commit_on_success
    def create_from_cart(self, cart, request):
        """
        This creates a new Order object with all its OrderItems using the current Cart object
        with its CartItems.
        """
        cart.update(request)
        order = self.model(user=cart.user, currency=cart.total.get_currency(),
            _subtotal=Decimal(0), _total=Decimal(0), stored_request=self.stored_request(request))
        order.save()
        for cart_item in cart.items.all():
            cart_item.update(request)
            order_item = OrderItemModel(order=order)
            if order_item.populate_from_cart_item(cart_item, request):
                order_item.save()
        order.populate_from_cart(cart, request)
        order.save()
        cart.delete()
        return order

    def stored_request(self, request):
        """
        Extract useful information about the request to be used for emulating a Django request
        during offline rendering.
        """
        return {
            'language': get_language_from_request(request),
            'absolute_base_uri': request.build_absolute_uri('/'),
            'remote_ip': get_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
        }

    def get_summary_url(self):
        """
        Returns the URL of the page with the list view for all orders related to the current user
        """
        if not hasattr(self, '_summary_url'):
            try:
                page = Page.objects.public().get(reverse_id='shop-order')
            except Page.DoesNotExist:
                page = Page.objects.public().filter(application_urls='OrderApp').first()
            finally:
                self._summary_url = page and page.get_absolute_url() or 'cms-page-with--reverse_id=shop-order--does-not-exist/'
        return self._summary_url

    def get_latest_url(self):
        """
        Returns the URL of the page with the detail view for the latest order related to the current user
        """
        try:
            return Page.objects.public().get(reverse_id='shop-order-last').get_absolute_url()
        except Page.DoesNotExist:
            pass  # TODO: could be retrieved by last order
        return 'cms-page-with--reverse_id=shop-order-last--does-not-exist/'


class WorkflowMixinMetaclass(deferred.ForeignKeyBuilder):
    """
    Add configured Workflow mixin classes to `OrderModel` and `OrderPayment` to customize
    all kinds of state transitions in a pluggable manner.
    """
    def __new__(cls, name, bases, attrs):
        if 'BaseOrder' in (b.__name__ for b in bases):
            bases = tuple(import_by_path(mc) for mc in shop_settings.ORDER_WORKFLOWS) + bases
            # merge the dicts of TRANSITION_TARGETS
            attrs['TRANSITION_TARGETS'] = {}
            for b in reversed(bases):
                TRANSITION_TARGETS = getattr(b, 'TRANSITION_TARGETS', {})
                if set(TRANSITION_TARGETS.keys()).intersection(attrs['TRANSITION_TARGETS']):
                    msg = "Mixin class {} already contains a transition named '{}'"
                    raise ImproperlyConfigured(msg.format(b.__name__, ', '.join(TRANSITION_TARGETS.keys())))
                attrs['TRANSITION_TARGETS'].update(TRANSITION_TARGETS)
        Model = super(WorkflowMixinMetaclass, cls).__new__(cls, name, bases, attrs)
        return Model


@python_2_unicode_compatible
class BaseOrder(with_metaclass(WorkflowMixinMetaclass, models.Model)):
    """
    An Order is the "in process" counterpart of the shopping cart, which freezes the state of the
    cart on the moment of purchase. It also holds stuff like the shipping and billing addresses,
    and keeps all the additional entities, as determined by the cart modifiers.
    """
    TRANSITION_TARGETS = {
        'new': _("New order without content"),
        'created': _("Order freshly created"),
    }
    decimalfield_kwargs = {
        'max_digits': 30,
        'decimal_places': 2,
    }
    decimal_exp = Decimal('.' + '0' * decimalfield_kwargs['decimal_places'])

    customer = deferred.ForeignKey('BaseCustomer', verbose_name=_("Customer"), related_name='orders')
    status = FSMField(default='new', protected=True, verbose_name=_("Status"))
    currency = models.CharField(max_length=7, editable=False,
        help_text=_("Currency in which this order was concluded"))
    _subtotal = models.DecimalField(verbose_name=_("Subtotal"), **decimalfield_kwargs)
    _total = models.DecimalField(verbose_name=_("Total"), **decimalfield_kwargs)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    extra = JSONField(default={}, verbose_name=_("Extra fields"),
        help_text=_("Arbitrary information for this order object on the moment of purchase."))
    stored_request = JSONField(default={},
        help_text=_("Parts of the Request objects on the moment of purchase."))
    objects = OrderManager()

    class Meta:
        abstract = True
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return "<{}(pk={})>".format(self.__class__.__name__, self.pk)

    @property
    def identifier(self):
        """
        Return a unique identifier representing this Order object.
        """
        msg = "Property method identifier() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    @property
    def subtotal(self):
        """
        The summed up amount for all ordered items excluding extra order lines.
        """
        return MoneyMaker(self.currency)(self._subtotal)

    @property
    def total(self):
        """
        The final total to charge for this order.
        """
        return MoneyMaker(self.currency)(self._total)

    @classmethod
    def round_amount(cls, amount):
        if amount.is_finite():
            return Decimal(amount).quantize(cls.decimal_exp, ROUND_UP)

    def get_absolute_url(self):
        """
        Returns the URL for the detail view of this order
        """
        return urljoin(OrderModel.objects.get_summary_url(), str(self.id))

    @transition(field=status, source='new', target='created')
    def populate_from_cart(self, cart, request):
        """
        Populate the order object with the fields from the given cart. Override this method,
        in case a customized cart has some fields which have to be transfered to the cart.
        """
        self._subtotal = Decimal(cart.subtotal)
        self._total = Decimal(cart.total)
        self.extra = dict(cart.extra)
        self.extra.update(rows=[(modifier, extra_row.data) for modifier, extra_row in cart.extra_rows.items()])

    def save(self, *args, **kwargs):
        """
        Before saving the Order object to the database, round the total to the given decimal_places
        """
        self._subtotal = BaseOrder.round_amount(self._subtotal)
        self._total = BaseOrder.round_amount(self._total)
        super(BaseOrder, self).save(*args, **kwargs)

    def get_amount_paid(self):
        """
        The amount paid is the sum of related orderpayments
        """
        amount = self.orderpayment_set.aggregate(amount=Sum('amount'))['amount']
        if amount is None:
            amount = MoneyMaker(self.currency)(0)
        return amount

    @classmethod
    def get_transition_name(cls, target):
        """Return the human readable name for a given transition target"""
        return cls.TRANSITION_TARGETS.get(target, target)

    def status_name(self):
        """Return the human readable name for the current transition state"""
        return self.TRANSITION_TARGETS.get(self.status, self.status)
    status_name.short_description = pgettext('status_name', "State")

OrderModel = deferred.MaterializedModel(BaseOrder)


class OrderPayment(with_metaclass(WorkflowMixinMetaclass, models.Model)):
    """
    A model to hold received payments for a given order.
    """
    order = deferred.ForeignKey(BaseOrder, verbose_name=_("Order"))
    status = FSMField(default='new', protected=True, verbose_name=_("Status"))
    amount = MoneyField(verbose_name=_("Amount paid"),
        help_text=_("How much was paid with this particular transfer."))
    transaction_id = models.CharField(max_length=255, verbose_name=_("Transaction ID"),
        help_text=_("The transaction processor's reference"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Received at"))
    payment_method = models.CharField(max_length=255, verbose_name=_("Payment method"),
        help_text=_("The payment backend used to process the purchase"))

    class Meta:
        verbose_name = _("Order payment")
        verbose_name_plural = _("Order payments")


class BaseOrderShipping(with_metaclass(WorkflowMixinMetaclass, models.Model)):
    """
    A model to keep track on the shipping of each order's item.
    """
    order = deferred.ForeignKey(BaseOrder, verbose_name=_("Order"))
    status = FSMField(default='new', protected=True, verbose_name=_("Status"))
    shipping_id = models.CharField(max_length=255, verbose_name=_("Shipping ID"),
        help_text=_("The transaction processor's reference"))
    shipping_method = models.CharField(max_length=255, verbose_name=_("Shipping method"),
        help_text=_("The shipping backend used to deliver the items for this order"))

    class Meta:
        abstract = True
        verbose_name = _("Shipping order")
        verbose_name_plural = _("Shipping orders")

OrderShippingModel = deferred.MaterializedModel(BaseOrderShipping)


class BaseOrderItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    An item for an order.
    """
    # TODO: add foreign key to OrderShipping
    order = deferred.ForeignKey(BaseOrder, related_name='items', verbose_name=_("Order"))
    product_identifier = models.CharField(max_length=255, verbose_name=_("Product identifier"),
        help_text=_("Product identifier at the moment of purchase."))
    product_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Product name"),
        help_text=_("Product name at the moment of purchase."))
    product = deferred.ForeignKey('BaseProduct', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("Product"))
    _unit_price = models.DecimalField(verbose_name=_("Unit price"), null=True,  # may be NaN
        help_text=_("Products unit price at the moment of purchase."), **BaseOrder.decimalfield_kwargs)
    _line_total = models.DecimalField(verbose_name=_("Line Total"), null=True,  # may be NaN
        help_text=_("Line total on the invoice at the moment of purchase."), **BaseOrder.decimalfield_kwargs)
    quantity = models.IntegerField(verbose_name=_("Ordered quantity"))
    extra = JSONField(default={}, verbose_name=_("Arbitrary information for this order item"))

    class Meta:
        abstract = True
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")

    @property
    def unit_price(self):
        return MoneyMaker(self.order.currency)(self._unit_price)

    @property
    def line_total(self):
        return MoneyMaker(self.order.currency)(self._line_total)

    def populate_from_cart_item(self, cart_item, request):
        """
        From a given cart item, populate the current order item.
        Return True if operation was successful, otherwise the order item is discarded.
        """
        self.product = cart_item.product
        self.product_name = cart_item.product.name  # store the name on the moment of purchase, in case it changes
        self.product_identifier = cart_item.product.identifier
        self._unit_price = Decimal(cart_item.product.get_price(request))
        self._line_total = Decimal(cart_item.line_total)
        self.quantity = cart_item.quantity
        self.extra = dict(cart_item.extra)
        self.extra.update(rows=[(modifier, extra_row.data) for modifier, extra_row in cart_item.extra_rows.items()])
        return True

    def save(self, *args, **kwargs):
        """
        Before saving the OrderItem object to the database, round the amounts to the given decimal places
        """
        self._unit_price = BaseOrder.round_amount(self._unit_price)
        self._line_total = BaseOrder.round_amount(self._line_total)
        super(BaseOrderItem, self).save(*args, **kwargs)

OrderItemModel = deferred.MaterializedModel(BaseOrderItem)
