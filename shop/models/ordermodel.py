# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from shop.models.cartmodel import CartItem
from shop.models.clientmodel import Client
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
        o.status = Order.STATUS_CODES[0][0] # Processing
        
        o.order_subtotal = cart.subtotal_price
        o.order_total = cart.total_price
        
        user = cart.user
        client = None
        
        if user:
            try:
                client = cart.user.client
            except Client.DoesNotExist:
                client = None
            
        if user and client:
            
            ship_address = cart.user.client.addresses.filter(is_shipping=True)[0] 
            bill_address = cart.user.client.addresses.filter(is_billing=True)[0]
        
        
            o.shipping_name = "%s %s" % (cart.user.first_name, cart.user.last_name)
            o.shipping_address = ship_address.address
            o.shipping_address2 = ship_address.address2
            o.shipping_city = ship_address.city
            o.shipping_zip_code = ship_address.zip_code
            o.shipping_state = ship_address.state
            o.shipping_country = ship_address.country.name
            
            o.billing_name = "%s %s" % (cart.user.first_name, cart.user.last_name)
            o.billing_address = bill_address.address
            o.billing_address2 = bill_address.address2
            o.billing_city = bill_address.city
            o.billing_zip_code = bill_address.zip_code
            o.billing_state = bill_address.state
            o.billing_country = bill_address.country.name
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
            i.unit_price = item.product.get_specific().get_price()
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
    CONFIRMED = 2 # Chosen shipping/payment backend, processing payment
    COMPLETED = 3 # Successful payment confirmed by payment backend
    SHIPPED = 4 # successful order shipped to client
    CANCELLED = 5 # order has been cancelled

    STATUS_CODES = (
        (PROCESSING, 'Processing'),
        (CONFIRMED, 'Confirmed'),
        (COMPLETED, 'Completed'),
        (SHIPPED, 'Shipped'),
        (CANCELLED, 'Cancelled'),
    )
    
    # If the user is null, the order was created with a session
    user = models.ForeignKey(User, blank=True, null=True)
    
    status = models.IntegerField(choices=STATUS_CODES, default=PROCESSING)
    
    order_subtotal = CurrencyField()
    order_total = CurrencyField()
    
    payment_method = models.CharField(max_length=255, null=True)
    
    # Addresses MUST be copied over to the order when it's created, however
    # the fields must be nullable since sometimes we cannot create the address 
    # fields right away (for instance when the shopper is a guest)
    shipping_name = models.CharField(max_length=255, null=True)
    shipping_address = models.CharField(max_length=255, null=True)
    shipping_address2 = models.CharField(max_length=255, null=True)
    shipping_city = models.CharField(max_length=255, null=True)
    shipping_zip_code = models.CharField(max_length=20, null=True)
    shipping_state = models.CharField(max_length=255, null=True)
    shipping_country = models.CharField(max_length=255, null=True)
    
    billing_name = models.CharField(max_length=255, null=True)
    billing_address = models.CharField(max_length=255, null=True)
    billing_address2 = models.CharField(max_length=255, null=True)
    billing_city = models.CharField(max_length=255, null=True)
    billing_zip_code = models.CharField(max_length=20, null=True)
    billing_state = models.CharField(max_length=255, null=True)
    billing_country = models.CharField(max_length=255, null=True)

    created = models.DateTimeField(auto_now_add=True,
            verbose_name=_('Created'))
    modified = models.DateTimeField(auto_now=True,
            verbose_name=_('Updated'))
    
    objects = OrderManager()
    
    class Meta:
        app_label = 'shop'
    
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


class OrderItem(models.Model):
    """
    A line Item for an order.
    """
    
    order = models.ForeignKey(Order, related_name='items')
    
    product_reference = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    unit_price = CurrencyField()
    quantity = models.IntegerField()
    
    line_subtotal = CurrencyField()
    line_total = CurrencyField()
    
    class Meta:
        app_label = 'shop'
    
    @property
    def product(self):
        return Product.objects.get(pk=self.product_reference)
    
class OrderExtraInfo(models.Model):
    """
    A holder for extra textual information to attach to this order.
    """
    order = models.ForeignKey(Order, related_name="extra_info")
    text = models.TextField()
    
    class Meta:
        app_label = 'shop'
        
class ExtraOrderPriceField(models.Model):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    order = models.ForeignKey(Order)
    label = models.CharField(max_length=255)
    value = CurrencyField()
    
    # Does this represent shipping costs?
    is_shipping = models.BooleanField(default=False, editable=False)

    class Meta:
        app_label = 'shop'
    
class ExtraOrderItemPriceField(models.Model):
    """
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    """
    order_item = models.ForeignKey(OrderItem)
    label = models.CharField(max_length=255)
    value = CurrencyField()
    
    class Meta:
        app_label = 'shop'
        
class OrderPayment(models.Model):
    """ 
    A class to hold basic payment information. Backends should define their own 
    more complex payment types should they need to store more informtion
    """
    order = models.ForeignKey(Order)
    amount = CurrencyField()# How much was payed with this particular transfer
    transaction_id = models.CharField(max_length=255, help_text="The transaction processor's reference")
    payment_method= models.CharField(max_length=255, help_text="The payment backend use to process the purchase")
    
    class Meta:
        app_label = 'shop'
