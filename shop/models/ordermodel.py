# -*- coding: utf-8 -*-
from django.db import models
from shop.models.cartmodel import CartItem
from shop.util.fields import CurrencyField

STATUS_CODES = (
    (1, 'Processing'), # User still checking out the contents
    (2, 'Confirmed'), # Contents are valid, now we can handle payment etc...
    (3, 'Completed'), # Everything is fine, only need to send the products
)

class OrderManager(models.Manager):
    
    def create_from_cart(self, cart):
        '''
        This creates a new Order object (and all the rest) from a passed Cart 
        object.
        
        Specifically, it creates an Order with corresponding OrderItems and
        eventually corresponding ExtraPriceFields
        
        '''
        # Let's create the Order itself:
        o = Order()
        o.status = STATUS_CODES[0][0] # Processing
        
        o.order_subtotal = cart.subtotal_price
        o.order_total = cart.subtotal_price
        
        ship_address = cart.user.client.addresses.filter(is_shipping=True)[0] 
        bill_address = cart.user.client.addresses.filter(is_billing=True)[0]
        
        o.shipping_name = str(cart.user.client)
        o.shipping_address = ship_address.address
        o.shipping_address2 = ship_address.address2
        o.shipping_zip_code = ship_address.zip_code
        o.shipping_state = ship_address.state
        o.shipping_country = ship_address.country.name
        
        o.billing_name = str(cart.user.client)
        o.billingaddress = bill_address.address
        o.billing_address2 = bill_address.address2
        o.billing_zip_code = bill_address.zip_code
        o.billing_state = bill_address.state
        o.billing_country = bill_address.country.name
        o.save()
        # There, now move on to the order items.
        
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            i = OrderItem()
            i.order = o
            i.product_name = item.product.name
            i.unit_price = item.product.unit_price
            i.quantity = item.quantity
            i.line_total = item.line_total
            i.line_subtotal = item.line_subtotal
            i.save()
        
        return o
        

class Order(models.Model):
    '''
    A model representing an Order.
    
    An order is the "in process" counterpart of the shopping cart, which holds
    stuff like the shipping and billing addresses (copied from the User profile)
    when the Order is first created), list of items, and holds stuff like the
    status, shipping costs, taxes, etc...
    '''
    
    status = models.IntegerField(choices=STATUS_CODES)
    
    order_subtotal = CurrencyField()
    order_total = CurrencyField()
    
    shipping_cost = CurrencyField()
    
    # Addresses MUST be copied over to the order when it's created.
    shipping_name = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255)
    shipping_zip_code = models.CharField(max_length=20)
    shipping_state = models.CharField(max_length=255)
    shipping_country = models.CharField(max_length=255)
    
    billing_name = models.CharField(max_length=255)
    billingaddress = models.CharField(max_length=255)
    billing_address2 = models.CharField(max_length=255)
    billing_zip_code = models.CharField(max_length=20)
    billing_state = models.CharField(max_length=255)
    billing_country = models.CharField(max_length=255)
    
    objects = OrderManager()
    
    class Meta:
        app_label = 'shop'

class OrderItem(models.Model):
    '''
    A line Item for an order.
    '''
    
    order = models.ForeignKey(Order, related_name='items')
    
    product_name = models.CharField(max_length=255)
    unit_price = CurrencyField()
    quantity = models.IntegerField()
    
    line_subtotal = CurrencyField()
    line_total = CurrencyField()
    
    class Meta:
        app_label = 'shop'
        
class ExtraOrderPriceField(models.Model):
    '''
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    '''
    order = models.ForeignKey(Order)
    label = models.CharField(max_length=255)
    value = CurrencyField()
    
    class Meta:
        app_label = 'shop'
    
class ExtraOrderItemPriceField(models.Model):
    '''
    This will make Cart-provided extra price fields persistent since we want
    to "snapshot" their statuses at the time when the order was made
    '''
    order_item = models.ForeignKey(OrderItem)
    label = models.CharField(max_length=255)
    value = CurrencyField()
    
    class Meta:
        app_label = 'shop'
        