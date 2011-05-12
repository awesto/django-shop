# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from shop.models.cartmodel import CartItem
from shop.models.productmodel import Product
from shop.util.fields import CurrencyField

class OrderManager(models.Manager):
    
    @transaction.commit_on_success
    def create_from_cart(self, cart):
        """
        This creates a new Order object (and all the rest) from a passed Cart 
        object.
        
        Specifically, it creates an Order with corresponding OrderItems and
        eventually corresponding ExtraPriceFields
        
        This will only actually commit the transaction once the function exits
        to minimize useless database access.
        
        """
        # Let's create the Order itself:
        o = Order()
        o.user = cart.user
        o.status = Order.PROCESSING # Processing
        
        o.order_subtotal = cart.subtotal_price
        o.order_total = cart.total_price
        
        o.save()
        
        # Let's serialize all the extra price arguments in DB
        for label, value in cart.extra_price_fields:
            eoi = ExtraOrderPriceField()
            eoi.order = o
            eoi.label = label
            eoi.value = value
            eoi.save()
        
        # There, now move on to the order items.
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            item.update()
            i = OrderItem()
            i.order = o
            i.product_reference = item.product.id
            i.product_name = item.product.name
            i.unit_price = item.product.get_price()
            i.quantity = item.quantity
            i.line_total = item.line_total
            i.line_subtotal = item.line_subtotal
            i.save()
            # For each order item, we save the extra_price_fields to DB 
            for label, value in item.extra_price_fields:
                eoi = ExtraOrderItemPriceField()
                eoi.order_item = i
                eoi.label = label
                eoi.value = value
                eoi.save()
        return o
        
class Order(models.Model):
    """
    A model representing an Order.
    
    An order is the "in process" counterpart of the shopping cart, which holds
    stuff like the shipping and billing addresses (copied from the User profile)
    when the Order is first created), list of items, and holds stuff like the
    status, shipping costs, taxes, etc...
    """
    
    PROCESSING = 1 # New order, no shipping/payment backend chosen yet
    PAYMENT = 2 # The user is filling in payment information
    CONFIRMED = 3 # Chosen shipping/payment backend, processing payment
    COMPLETED = 4 # Successful payment confirmed by payment backend
    SHIPPED = 5 # successful order shipped to client
    CANCELLED = 6 # order has been cancelled

    STATUS_CODES = (
        (PROCESSING, 'Processing'),
        (PAYMENT, 'Selecting payment'),
        (CONFIRMED, 'Confirmed'),
        (COMPLETED, 'Completed'),
        (SHIPPED, 'Shipped'),
        (CANCELLED, 'Cancelled'),
    )
    
    # If the user is null, the order was created with a session
    user = models.ForeignKey(User, blank=True, null=True,
            verbose_name=_('User'))
    
    status = models.IntegerField(choices=STATUS_CODES, default=PROCESSING,
            verbose_name=_('Status'))
    
    order_subtotal = CurrencyField(verbose_name=_('Order subtotal'))
    order_total = CurrencyField(verbose_name='Order total')
    
    payment_method = models.CharField(max_length=255, null=True,
            verbose_name=_('Payment method'))
    
    # Addresses MUST be copied over to the order when it's created, however
    # the fields must be nullable since sometimes we cannot create the address 
    # fields right away (for instance when the shopper is a guest)
    shipping_name = models.CharField(max_length=255, null=True,
            verbose_name=_('Shipping name'))
    shipping_address = models.CharField(max_length=255, null=True,
            verbose_name=_('Shipping address'))
    shipping_address2 = models.CharField(max_length=255, null=True,
            verbose_name=_('Shipping addresses 2'))
    shipping_city = models.CharField(max_length=255, null=True,
            verbose_name=_('Shipping City'))
    shipping_zip_code = models.CharField(max_length=20, null=True,
            verbose_name=_('Shipping zip code'))
    shipping_state = models.CharField(max_length=255, null=True,
            verbose_name=_('Shipping state'))
    shipping_country = models.CharField(max_length=255, null=True,
            verbose_name=_('Shipping country'))
    
    billing_name = models.CharField(max_length=255, null=True,
            verbose_name=_('Billing name'))
    billing_address = models.CharField(max_length=255, null=True,
            verbose_name=_('Billing address'))
    billing_address2 = models.CharField(max_length=255, null=True,
            verbose_name=_('Billing address 2'))
    billing_city = models.CharField(max_length=255, null=True,
            verbose_name=_('Billing city'))
    billing_zip_code = models.CharField(max_length=20, null=True,
            verbose_name=_('Billing zip code'))
    billing_state = models.CharField(max_length=255, null=True,
            verbose_name=_('Billing state'))
    billing_country = models.CharField(max_length=255, null=True,
            verbose_name=_('Billing country'))

    created = models.DateTimeField(auto_now_add=True,
            verbose_name=_('Created'))
    modified = models.DateTimeField(auto_now=True,
            verbose_name=_('Updated'))
    
    objects = OrderManager()
    
    class Meta:
        app_label = 'shop'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
    
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
        sum = OrderPayment.objects.filter(order=self).aggregate(sum=Sum('amount'))
        result = sum.get('sum')
        if not result:
            result = Decimal('0')
        return result
        
    @property
    def shipping_costs(self):
        sum = Decimal('0.0')
        cost_list = ExtraOrderPriceField.objects.filter(order=self).filter(is_shipping=True)
        for cost in cost_list:
            sum = sum + cost.value
        return sum

    def __unicode__(self):
        return _('Order ID: %(id)s') % {'id': self.id}

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk })

    def set_billing_address(self, address):
        self.billing_name = "%s %s" % (self.user.first_name, self.user.last_name)
        self.billing_address = address.address
        self.billing_address2 = address.address2
        self.billing_city = address.city
        self.billing_zip_code = address.zip_code
        self.billing_state = address.state
        self.billing_country = address.country.name
        self.save()
    
    def set_shipping_address(self, address):
        self.shipping_name = "%s %s" % (self.user.first_name, self.user.last_name)
        self.shipping_address = address.address
        self.shipping_address2 = address.address2
        self.shipping_city = address.city
        self.shipping_zip_code = address.zip_code
        self.shipping_state = address.state
        self.shipping_country = address.country.name
        self.save()

class OrderItem(models.Model):
    """
    A line Item for an order.
    """
    
    order = models.ForeignKey(Order, related_name='items',
            verbose_name=_('Order'))
    
    product_reference = models.CharField(max_length=255,
            verbose_name=_('Product reference'))
    product_name = models.CharField(max_length=255,
            verbose_name=_('Product name'))
    unit_price = CurrencyField(verbose_name=_('Unit price'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    
    line_subtotal = CurrencyField(verbose_name=_('Line subtotal'))
    line_total = CurrencyField(verbose_name=_('Line total'))
    
    class Meta:
        app_label = 'shop'
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')
    
    @property
    def product(self):
        return Product.objects.get(pk=self.product_reference)


class OrderExtraInfo(models.Model):
    """
    A holder for extra textual information to attach to this order.
    """
    order = models.ForeignKey(Order, related_name="extra_info",
            verbose_name=_('Order'))
    text = models.TextField(verbose_name=_('Extra info'))

    class Meta:
        app_label = 'shop'
        verbose_name = _('Order extra info')
        verbose_name_plural = _('Order extra info')


class ExtraOrderPriceField(models.Model):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    value = CurrencyField(verbose_name=_('Amount'))
    
    # Does this represent shipping costs?
    is_shipping = models.BooleanField(default=False, editable=False,
            verbose_name=_('Is shipping'))

    class Meta:
        app_label = 'shop'
        verbose_name = _('Extra order price field')
        verbose_name_plural = _('Extra order price fields')


class ExtraOrderItemPriceField(models.Model):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    order_item = models.ForeignKey(OrderItem, verbose_name=_('Order item'))
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    value = CurrencyField(verbose_name=_('Amount'))
    
    class Meta:
        app_label = 'shop'
        verbose_name = _('Extra order item price field')
        verbose_name_plural = _('Extra order item price fields')


class OrderPayment(models.Model):
    """ 
    A class to hold basic payment information. Backends should define their own 
    more complex payment types should they need to store more informtion
    """
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    amount = CurrencyField(verbose_name=_('Amount'))# How much was payed with this particular transfer
    transaction_id = models.CharField(max_length=255, 
            verbose_name=_('Transaction ID'),
            help_text=_("The transaction processor's reference"))
    payment_method = models.CharField(max_length=255,
            verbose_name=_('Payment method'),
            help_text=_("The payment backend use to process the purchase"))
    
    class Meta:
        app_label = 'shop'
        verbose_name = _('Order payment')
        verbose_name_plural = _('Order payments')
