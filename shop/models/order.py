# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import logging
from six import with_metaclass
from django.core import checks
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.db.models.aggregates import Sum
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _, pgettext_lazy, get_language_from_request
from django.utils.six.moves.urllib.parse import urljoin
from django_fsm import FSMField, transition
from ipware.ip import get_ip
from cms.models import Page
from shop.conf import app_settings
from shop.models.cart import CartItemModel
from shop.models.fields import JSONField
from shop.money.fields import MoneyField, MoneyMaker
from shop import deferred
from shop.models.product import BaseProduct


class OrderQuerySet(models.QuerySet):
    def _filter_or_exclude(self, negate, *args, **kwargs):
        """
        Emulate filter queries on the Order model using a pseudo slug attribute.
        This allows to use order numbers as slugs, formatted by method `Order.get_number()`.
        """
        lookup_kwargs = {}
        for key, lookup in kwargs.items():
            try:
                index = key.index('__')
                field_name, lookup_type = key[:index], key[index:]
            except ValueError:
                field_name, lookup_type = key, ''
            if field_name == 'slug':
                key, lookup = self.model.resolve_number(lookup).popitem()
                lookup_kwargs.update({key + lookup_type: lookup})
            else:
                lookup_kwargs.update({key: lookup})
        return super(OrderQuerySet, self)._filter_or_exclude(negate, *args, **lookup_kwargs)


class OrderManager(models.Manager):
    _queryset_class = OrderQuerySet

    def create_from_cart(self, cart, request):
        """
        This creates a new empty Order object with a valid order number (many payment service
        providers require an order number, before the purchase is actually completed). Therefore
        the order is not populated with any cart items yet; this must be performed in the next step
        by calling ``order.populate_from_cart(cart, request)``, otherwise the order object remains
        in state ``new``. The latter can happen, if a payment service provider did not acknowledge
        a payment, hence the items remain in the cart.
        """
        cart.update(request)
        cart.customer.get_or_assign_number()
        order = self.model(
            customer=cart.customer,
            currency=cart.total.currency,
            _subtotal=Decimal(0),
            _total=Decimal(0),
            stored_request=self.stored_request(request),
        )
        order.get_or_assign_number()
        order.assign_secret()
        order.save()
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
        Returns the URL of the page with the list view for all orders related to the current customer
        """
        if not hasattr(self, '_summary_url'):
            try:  # via CMS pages
                page = Page.objects.public().get(reverse_id='shop-order')
            except Page.DoesNotExist:
                page = Page.objects.public().filter(application_urls='OrderApp').first()
            if page:
                self._summary_url = page.get_absolute_url()
            else:
                try:  # through hardcoded urlpatterns
                    self._summary_url = reverse('shop-order')
                except NoReverseMatch:
                    self._summary_url = '/cms-page_or_view_with__reverse_id=shop-order__does_not_exist/'
        return self._summary_url


class WorkflowMixinMetaclass(deferred.ForeignKeyBuilder):
    """
    Add configured Workflow mixin classes to ``OrderModel`` and ``OrderPayment`` to customize
    all kinds of state transitions in a pluggable manner.
    """

    def __new__(cls, name, bases, attrs):
        if 'BaseOrder' in (b.__name__ for b in bases):
            bases = tuple(app_settings.ORDER_WORKFLOWS) + bases
            # merge the dicts of TRANSITION_TARGETS
            attrs.update(_transition_targets={}, _auto_transitions={})
            for b in reversed(bases):
                TRANSITION_TARGETS = getattr(b, 'TRANSITION_TARGETS', {})
                try:
                    delattr(b, 'TRANSITION_TARGETS')
                except AttributeError:
                    pass
                if set(TRANSITION_TARGETS.keys()).intersection(attrs['_transition_targets']):
                    msg = "Mixin class {} already contains a transition named '{}'"
                    raise ImproperlyConfigured(msg.format(b.__name__, ', '.join(TRANSITION_TARGETS.keys())))
                attrs['_transition_targets'].update(TRANSITION_TARGETS)
                attrs['_auto_transitions'].update(cls.add_to_auto_transitions(b))
        Model = super(WorkflowMixinMetaclass, cls).__new__(cls, name, bases, attrs)
        return Model

    @classmethod
    def add_to_auto_transitions(cls, base):
        result = {}
        for name, method in base.__dict__.items():
            if callable(method) and hasattr(method, '_django_fsm'):
                for name, transition in method._django_fsm.transitions.items():
                    if transition.custom.get('auto'):
                        result.update({name: method})
        return result


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
        'payment_confirmed': _("Payment confirmed"),
        'payment_declined': _("Payment declined"),
    }
    decimalfield_kwargs = {
        'max_digits': 30,
        'decimal_places': 2,
    }
    decimal_exp = Decimal('.' + '0' * decimalfield_kwargs['decimal_places'])

    customer = deferred.ForeignKey(
        'BaseCustomer',
        verbose_name=_("Customer"),
        related_name='orders',
        on_delete=models.PROTECT,
    )

    status = FSMField(
        default='new',
        protected=True,
        verbose_name=_("Status"),
    )

    currency = models.CharField(
        max_length=7,
        editable=False,
        help_text=_("Currency in which this order was concluded"),
    )

    _subtotal = models.DecimalField(
        _("Subtotal"),
        **decimalfield_kwargs
    )

    _total = models.DecimalField(
        _("Total"),
        **decimalfield_kwargs
    )

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )

    extra = JSONField(
        verbose_name=_("Extra fields"),
        help_text=_("Arbitrary information for this order object on the moment of purchase."),
    )

    stored_request = JSONField(
        help_text=_("Parts of the Request objects on the moment of purchase."),
    )

    objects = OrderManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseOrder, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger('shop.order')

    def __str__(self):
        return self.get_number()

    def __repr__(self):
        return "<{}(pk={})>".format(self.__class__.__name__, self.pk)

    def get_or_assign_number(self):
        """
        Hook to get or to assign the order number. It shall be invoked, every time an Order
        object is created. If you prefer to use an order number which differs from the primary
        key, then override this method.
        """
        return self.get_number()

    def get_number(self):
        """
        Hook to get the order number.
        A class inheriting from Order may transform this into a string which is better readable.
        """
        return str(self.pk)

    def assign_secret(self):
        """
        Hook to assign a secret to authorize access on this Order object without authentication.
        """

    @property
    def secret(self):
        """
        Hook to return a secret if available.
        """

    @classmethod
    def resolve_number(cls, number):
        """
        Return a lookup pair used to filter down a queryset.
        It should revert the effect from the above method `get_number`.
        """
        return dict(pk=number)

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
            return Decimal(amount).quantize(cls.decimal_exp)

    def get_absolute_url(self):
        """
        Returns the URL for the detail view of this order.
        """
        return urljoin(OrderModel.objects.get_summary_url(), self.get_number())

    @transaction.atomic
    @transition(field=status, source='new', target='created')
    def populate_from_cart(self, cart, request):
        """
        Populate the order object with the fields from the given cart.
        For each cart item a corresponding order item is created populating its fields and removing
        that cart item.

        Override this method, in case a customized cart has some fields which have to be transfered
        to the cart.
        """
        assert hasattr(cart, 'subtotal') and hasattr(cart, 'total'), \
            "Did you forget to invoke 'cart.update(request)' before populating from cart?"
        for cart_item in cart.items.all():
            cart_item.update(request)
            order_item = OrderItemModel(order=self)
            try:
                order_item.populate_from_cart_item(cart_item, request)
                order_item.save()
                cart_item.delete()
            except CartItemModel.DoesNotExist:
                pass
        self._subtotal = Decimal(cart.subtotal)
        self._total = Decimal(cart.total)
        self.extra = dict(cart.extra)
        self.extra.update(rows=[(modifier, extra_row.data) for modifier, extra_row in cart.extra_rows.items()])
        self.save()

    @transaction.atomic
    def readd_to_cart(self, cart):
        """
        Re-add the items of this order back to the cart.
        """
        for order_item in self.items.all():
            extra = dict(order_item.extra)
            extra.pop('rows', None)
            extra.update(product_code=order_item.product_code)
            cart_item = order_item.product.is_in_cart(cart, **extra)
            if cart_item:
                cart_item.quantity = max(cart_item.quantity, order_item.quantity)
            else:
                cart_item = CartItemModel(cart=cart, product=order_item.product,
                                          product_code=order_item.product_code,
                                          quantity=order_item.quantity, extra=extra)
            cart_item.save()

    def save(self, with_notification=False, **kwargs):
        """
        :param with_notification: If ``True``, all notifications for the state of this Order object
        are executed.
        """
        from shop.transition import transition_change_notification

        auto_transition = self._auto_transitions.get(self.status)
        if callable(auto_transition):
            auto_transition(self)

        # round the total to the given decimal_places
        self._subtotal = BaseOrder.round_amount(self._subtotal)
        self._total = BaseOrder.round_amount(self._total)
        super(BaseOrder, self).save(**kwargs)
        if with_notification:
            transition_change_notification(self)

    @cached_property
    def amount_paid(self):
        """
        The amount paid is the sum of related orderpayments
        """
        amount = self.orderpayment_set.aggregate(amount=Sum('amount'))['amount']
        if amount is None:
            amount = MoneyMaker(self.currency)()
        return amount

    @property
    def outstanding_amount(self):
        """
        Return the outstanding amount paid for this order
        """
        return self.total - self.amount_paid

    def is_fully_paid(self):
        return self.amount_paid >= self.total

    @transition(field='status', source='*', target='payment_confirmed', conditions=[is_fully_paid])
    def acknowledge_payment(self, by=None):
        """
        Change status to ``payment_confirmed``. This status code is known globally and can be used
        by all external plugins to check, if an Order object has been fully paid.
        """
        self.logger.info("Acknowledge payment by user %s", by)

    def cancelable(self):
        """
        A hook method to be overridden by mixin classes managing Order cancellations.

        :returns: ``True`` if the current Order is cancelable.
        """
        return False

    def refund_payment(self):
        """
        Hook to handle payment refunds.
        """

    def withdraw_from_delivery(self):
        """
        Hook to withdraw shipping order.
        """

    @classmethod
    def get_all_transitions(cls):
        """
        :returns: A generator over all transition objects for this Order model.
        """
        return cls.status.field.get_all_transitions(OrderModel)

    @classmethod
    def get_transition_name(cls, target):
        """
        :returns: The verbose name for a given transition target.
        """
        return cls._transition_targets.get(target, target)

    def status_name(self):
        """
        :returns: The verbose name for the current transition state.
        """
        return self._transition_targets.get(self.status, self.status)

    status_name.short_description = pgettext_lazy('order_models', "State")

OrderModel = deferred.MaterializedModel(BaseOrder)


@python_2_unicode_compatible
class OrderPayment(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    A model to hold received payments for a given order.
    """
    order = deferred.ForeignKey(
        BaseOrder,
        verbose_name=_("Order"),
    )

    amount = MoneyField(
        _("Amount paid"),
        help_text=_("How much was paid with this particular transfer."),
    )

    transaction_id = models.CharField(
        _("Transaction ID"),
        max_length=255,
        help_text=_("The transaction processor's reference"),
    )

    created_at = models.DateTimeField(
        _("Received at"),
        auto_now_add=True,
    )

    payment_method = models.CharField(
        _("Payment method"),
        max_length=50,
        help_text=_("The payment backend used to process the purchase"),
    )

    class Meta:
        verbose_name = pgettext_lazy('order_models', "Order payment")
        verbose_name_plural = pgettext_lazy('order_models', "Order payments")

    def __str__(self):
        return _("Payment ID: {}").format(self.id)


@python_2_unicode_compatible
class BaseOrderItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    An item for an order.
    """
    order = deferred.ForeignKey(
        BaseOrder,
        related_name='items',
        verbose_name=_("Order"),
    )

    product_name = models.CharField(
        _("Product name"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Product name at the moment of purchase."),
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Product code at the moment of purchase."),
    )

    product = deferred.ForeignKey(
        BaseProduct,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Product"),
    )

    _unit_price = models.DecimalField(
        _("Unit price"),
        null=True,  # may be NaN
        help_text=_("Products unit price at the moment of purchase."),
        **BaseOrder.decimalfield_kwargs
    )

    _line_total = models.DecimalField(
        _("Line Total"),
        null=True,  # may be NaN
        help_text=_("Line total on the invoice at the moment of purchase."),
        **BaseOrder.decimalfield_kwargs
    )

    extra = JSONField(
        verbose_name=_("Extra fields"),
        help_text=_("Arbitrary information for this order item"),
    )

    class Meta:
        abstract = True
        verbose_name = pgettext_lazy('order_models', "Ordered Item")
        verbose_name_plural = pgettext_lazy('order_models', "Ordered Items")

    def __str__(self):
        return self.product_name

    @classmethod
    def check(cls, **kwargs):
        errors = super(BaseOrderItem, cls).check(**kwargs)
        for cart_field in CartItemModel._meta.fields:
            if cart_field.attname == 'quantity':
                break
        else:
            msg = "Class `{}` must implement a field named `quantity`."
            errors.append(checks.Error(msg.format(CartItemModel.__name__)))
        for field in cls._meta.fields:
            if field.attname == 'quantity':
                if field.get_internal_type() != cart_field.get_internal_type():
                    msg = "Field `{}.quantity` must be of same type as `{}.quantity`."
                    errors.append(checks.Error(msg.format(cls.__name__, CartItemModel.__name__)))
                break
        else:
            msg = "Class `{}` must implement a field named `quantity`."
            errors.append(checks.Error(msg.format(cls.__name__)))
        return errors

    @property
    def unit_price(self):
        return MoneyMaker(self.order.currency)(self._unit_price)

    @property
    def line_total(self):
        return MoneyMaker(self.order.currency)(self._line_total)

    def populate_from_cart_item(self, cart_item, request):
        """
        From a given cart item, populate the current order item.
        If the operation was successful, the given item shall be removed from the cart.
        If a CartItem.DoesNotExist exception is raised, discard the order item.
        """
        if cart_item.quantity == 0:
            raise CartItemModel.DoesNotExist("Cart Item is on the Wish List")
        self.product = cart_item.product
        # for historical integrity, store the product's name and price at the moment of purchase
        self.product_name = cart_item.product.product_name
        self.product_code = cart_item.product_code
        self._unit_price = Decimal(cart_item.unit_price)
        self._line_total = Decimal(cart_item.line_total)
        self.quantity = cart_item.quantity
        self.extra = dict(cart_item.extra)
        extra_rows = [(modifier, extra_row.data) for modifier, extra_row in cart_item.extra_rows.items()]
        self.extra.update(rows=extra_rows)

    def save(self, *args, **kwargs):
        """
        Before saving the OrderItem object to the database, round the amounts to the given decimal places
        """
        self._unit_price = BaseOrder.round_amount(self._unit_price)
        self._line_total = BaseOrder.round_amount(self._line_total)
        super(BaseOrderItem, self).save(*args, **kwargs)

OrderItemModel = deferred.MaterializedModel(BaseOrderItem)
