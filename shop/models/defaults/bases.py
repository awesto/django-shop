# -*- coding: utf-8 -*-
from decimal import Decimal
from distutils.version import LooseVersion
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from polymorphic.polymorphic_model import PolymorphicModel
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.util.fields import CurrencyField
from shop.util.loader import get_model_string
import django


#==============================================================================
# Product
#==============================================================================
class BaseProduct(PolymorphicModel):
    """
    A basic product for the shop
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property
    """

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'), unique=True)
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    date_added = models.DateTimeField(auto_now_add=True,
        verbose_name=_('Date added'))
    last_modified = models.DateTimeField(auto_now=True,
        verbose_name=_('Last modified'))
    unit_price = CurrencyField(verbose_name=_('Unit price'))

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def get_price(self):
        """
        Return the price for this item (provided for extensibility)
        """
        return self.unit_price

    def get_name(self):
        """
        Return the name of this Product (provided for extensibility)
        """
        return self.name


#==============================================================================
# Carts
#==============================================================================
class BaseCart(models.Model):
    """
    This should be a rather simple list of items. Ideally it should be bound to
    a session and not to a User is we want to let people buy from our shop
    without having to register with us.
    """
    # If the user is null, that means this is used for a session
    user = models.OneToOneField(User, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __init__(self, *args, **kwargs):
        super(BaseCart, self).__init__(*args, **kwargs)
        # That will hold things like tax totals or total discount
        self.subtotal_price = Decimal('0.0')
        self.total_price = Decimal('0.0')
        self.current_total = Decimal('0.0')  # used by cart modifiers
        self.extra_price_fields = []  # List of tuples (label, value)
        self._updated_cart_items = None

    def add_product(self, product, quantity=1, merge=True, queryset=None):
        """
        Adds a (new) product to the cart.

        The parameter `merge`, controls wheter we should merge the added
        CartItem with another already existing sharing the same
        product_id. This is useful when you have products with variations
        (for example), and you don't want to have your products merge (to loose
        their specific variations, for example).

        A drawback is, that generally  setting `merge` to ``False`` for
        products with variations can be a problem if users can buy thousands of
        products at a time (that would mean we would create thousands of
        CartItems as well which all have the same variation).

        The parameter `queryset` can be used to override the standard queryset
        that is being used to find the CartItem that should be merged into.
        If you use variations, just finding the first CartItem that
        belongs to this cart and the given product is not sufficient. You will
        want to find the CartItem that already has the same variations that the
        user chose for this request.

        Example with merge = True:
        >>> self.items[0] = CartItem.objects.create(..., product=MyProduct())
        >>> self.add_product(MyProduct())
        >>> self.items[0].quantity
        2

        Example with merge=False:
        >>> self.items[0] = CartItem.objects.create(..., product=MyProduct())
        >>> self.add_product(MyProduct())
        >>> self.items[0].quantity
        1
        >>> self.items[1].quantity
        1
        """
        from shop.models import CartItem
        if queryset == None:
            queryset = CartItem.objects.filter(cart=self, product=product)
        item = queryset
        # Let's see if we already have an Item with the same product ID
        if item.exists() and merge:
            cart_item = item[0]
            cart_item.quantity = cart_item.quantity + int(quantity)
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=self, quantity=quantity, product=product)
            cart_item.save()

        self.save()  # to get the last updated timestamp
        return cart_item

    def update_quantity(self, cart_item_id, quantity):
        """
        Updates the quantity for given cart item or deletes it if its quantity
        reaches `0`
        """
        cart_item = self.items.get(pk=cart_item_id)
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        self.save()
        return cart_item

    def delete_item(self, cart_item_id):
        """
        A simple convenience method to delete one of the cart's items. This
        allows to implicitely check for "access rights" since we insure the
        cartitem is actually in the user's cart
        """
        cart_item = self.items.get(pk=cart_item_id)
        cart_item.delete()
        self.save()

    def get_updated_cart_items(self):
        """
        Returns updated cart items after update() has been called and
        cart modifiers have been processed for all cart items.
        """
        assert self._updated_cart_items is not None, ('Cart needs to be'
            'updated before calling get_updated_cart_items.')
        return self._updated_cart_items

    def update(self, state=None):
        """
        This should be called whenever anything is changed in the cart (added
        or removed).
        It will loop on all line items in the cart, and call all the price
        modifiers on each row.
        After doing this, it will compute and update the order's total and
        subtotal fields, along with any payment field added along the way by
        modifiers.

        Note that theses added fields are not stored - we actually want to
        reflect rebate and tax changes on the *cart* items, but we don't want
        that for the order items (since they are legally binding after the
        "purchase" button was pressed)
        """
        from shop.models import CartItem, Product

        # This is a ghetto "select_related" for polymorphic models.
        items = CartItem.objects.filter(cart=self)
        product_ids = [item.product_id for item in items]
        products = Product.objects.filter(id__in=product_ids)
        products_dict = dict([(p.id, p) for p in products])

        self.extra_price_fields = []  # Reset the price fields
        self.subtotal_price = Decimal('0.0')  # Reset the subtotal

        # This will hold extra information that cart modifiers might want to
        # pass to each other
        if state == None:
            state = {}

        # This calls all the pre_process_cart methods (if any), before the cart
        # is processed. This allows for data collection on the cart for
        # example)
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.pre_process_cart(self, state)

        for item in items:  # For each CartItem (order line)...
            # This is still the ghetto select_related
            item.product = products_dict[item.product_id]
            self.subtotal_price = self.subtotal_price + item.update(state)

        self.current_total = self.subtotal_price
        # Now we have to iterate over the registered modifiers again
        # (unfortunately) to pass them the whole Order this time
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.process_cart(self, state)

        self.total_price = self.current_total

        # This calls the post_process_cart method from cart modifiers, if any.
        # It allows for a last bit of processing on the "finished" cart, before
        # it is displayed
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.post_process_cart(self, state)

        # Cache updated cart items
        self._updated_cart_items = items

    def empty(self):
        """
        Remove all cart items
        """
        self.items.all().delete()
        self.delete()

    @property
    def total_quantity(self):
        """
        Returns the total quantity of all items in the cart
        """
        return sum([ci.quantity for ci in self.items.all()])


class BaseCartItem(models.Model):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased :)
    """
    cart = models.ForeignKey(get_model_string('Cart'), related_name="items")

    quantity = models.IntegerField()

    product = models.ForeignKey(get_model_string('Product'))

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')

    def __init__(self, *args, **kwargs):
        # That will hold extra fields to display to the user
        # (ex. taxes, discount)
        super(BaseCartItem, self).__init__(*args, **kwargs)
        self.extra_price_fields = []  # list of tuples (label, value)
        # These must not be stored, since their components can be changed
        # between sessions / logins etc...
        self.line_subtotal = Decimal('0.0')
        self.line_total = Decimal('0.0')
        self.current_total = Decimal('0.0')  # Used by cart modifiers

    def update(self, state):
        self.extra_price_fields = []  # Reset the price fields
        self.line_subtotal = self.product.get_price() * self.quantity
        self.current_total = self.line_subtotal

        for modifier in cart_modifiers_pool.get_modifiers_list():
            # We now loop over every registered price modifier,
            # most of them will simply add a field to extra_payment_fields
            modifier.process_cart_item(self, state)

        self.line_total = self.current_total
        return self.line_total


#==============================================================================
# Orders
#==============================================================================
class BaseOrder(models.Model):
    """
    A model representing an Order.

    An order is the "in process" counterpart of the shopping cart, which holds
    stuff like the shipping and billing addresses (copied from the User
    profile) when the Order is first created), list of items, and holds stuff
    like the status, shipping costs, taxes, etc...
    """

    PROCESSING = 1  # New order, no shipping/payment backend chosen yet
    PAYMENT = 2  # The user is filling in payment information
    CONFIRMED = 3  # Chosen shipping/payment backend, processing payment
    COMPLETED = 4  # Successful payment confirmed by payment backend
    SHIPPED = 5  # successful order shipped to client
    CANCELLED = 6  # order has been cancelled

    STATUS_CODES = (
        (PROCESSING, _('Processing')),
        (PAYMENT, _('Selecting payment')),
        (CONFIRMED, _('Confirmed')),
        (COMPLETED, _('Completed')),
        (SHIPPED, _('Shipped')),
        (CANCELLED, _('Cancelled')),
    )

    # If the user is null, the order was created with a session
    user = models.ForeignKey(User, blank=True, null=True,
            verbose_name=_('User'))
    status = models.IntegerField(choices=STATUS_CODES, default=PROCESSING,
            verbose_name=_('Status'))
    order_subtotal = CurrencyField(verbose_name=_('Order subtotal'))
    order_total = CurrencyField(verbose_name=_('Order Total'))
    shipping_address_text = models.TextField(_('Shipping address'), blank=True,
        null=True)
    billing_address_text = models.TextField(_('Billing address'), blank=True,
        null=True)
    created = models.DateTimeField(auto_now_add=True,
            verbose_name=_('Created'))
    modified = models.DateTimeField(auto_now=True,
            verbose_name=_('Updated'))

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __unicode__(self):
        return _('Order ID: %(id)s') % {'id': self.id}

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def is_payed(self):
        """Has this order been integrally payed for?"""
        return self.amount_payed == self.order_total

    def is_completed(self):
        return self.status == self.COMPLETED

    @property
    def amount_payed(self):
        """
        The amount payed is the sum of related orderpayments
        """
        from shop.models import OrderPayment
        sum_ = OrderPayment.objects.filter(order=self).aggregate(
                sum=Sum('amount'))
        result = sum_.get('sum')
        if not result:
            result = Decimal('-1')
        return result

    @property
    def shipping_costs(self):
        from shop.models import ExtraOrderPriceField
        sum_ = Decimal('0.0')
        cost_list = ExtraOrderPriceField.objects.filter(order=self).filter(
                is_shipping=True)
        for cost in cost_list:
            sum_ += cost.value
        return sum_

    def set_billing_address(self, billing_address):
        """
        Process billing_address trying to get as_text method from address
        and copying.
        You can override this method to process address more granulary
        e.g. you can copy address instance and save FK to it in your order
        class.
        """
        if  hasattr(billing_address, 'as_text'):
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
        if hasattr(shipping_address, 'as_text'):
            self.shipping_address_text = shipping_address.as_text()
            self.save()


# We need some magic to support django < 1.3 that has no support
# models.on_delete option
f_kwargs = {}
if LooseVersion(django.get_version()) >= LooseVersion('1.3'):
    f_kwargs['on_delete'] = models.SET_NULL


class BaseOrderItem(models.Model):
    """
    A line Item for an order.
    """

    order = models.ForeignKey(get_model_string('Order'), related_name='items',
            verbose_name=_('Order'))
    product_reference = models.CharField(max_length=255,
            verbose_name=_('Product reference'))
    product_name = models.CharField(max_length=255, null=True, blank=True,
            verbose_name=_('Product name'))
    product = models.ForeignKey(get_model_string('Product'),
        verbose_name=_('Product'), null=True, blank=True, **f_kwargs)
    unit_price = CurrencyField(verbose_name=_('Unit price'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    line_subtotal = CurrencyField(verbose_name=_('Line subtotal'))
    line_total = CurrencyField(verbose_name=_('Line total'))

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')

    def save(self, *args, **kwargs):
        if not self.product_name and self.product:
            self.product_name = self.product.get_name()
        super(BaseOrderItem, self).save(*args, **kwargs)
