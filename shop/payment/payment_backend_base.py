# -*- coding: utf-8 -*-

'''
This file defines the interafces one should implement when either creating a new
payment module or willing to use modules with another shop system.
'''
from decimal import Decimal
from django.http import HttpResponseRedirect
from shop.backend_base import BaseBackendAPI
from shop.models.ordermodel import Order

class PaymentBackendAPI(BaseBackendAPI):
    '''
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    payment plugins are interchangeable between systems.
    
    This implementation is the interface reference for Django Shop
    
    Methods defined in BaseBackendAPI:
    getOrder(request): Return the Order object for the current shopper
    
    '''
    
    def confirm_payment(self, order, amount, transaction_id, save=True):
        '''
        Marks the specified amount for the given order as payed.
        This allows to hook in more complex behaviors (like saving a history
        of payments in a Payment model)
        The optional save argument allows backends to explicitly not save the 
        order yet
        '''
        # TODO: Add a "Payment" model to handle this in a more professional way
        # TODO: Add the transaction ID to the payment object, too.
        # TODO: Add a description of the payment type used (maybe the backend's name)
        amount = Decimal(amount) # In case it's not already a Decimal
        order.amount_payed = order.amount_payed + amount
        if save:
            order.save()
        
    def set_payment_method(self, order, method, save=True):
        '''
        Sets the payment method on the order object to whatever is specified in
        the method argument (should be a String)
        '''
        order.payment_method = method
        if save:
            order.save()
    
    def is_order_payed(self, order):
        '''Whether the passed order is fully payed or not.'''
        return order.is_payed()
    
    def is_order_complete(self, order):
        return order.is_complete()
    
    def get_order_total(self, order):
        '''The total amount to be charged for passed order'''
        return order.order_total
    
    def get_order_short_name(self, order):
        '''A short name for the order, to be displayed on the payment processor's
        website. Should be human-readable, as much as possible'''
        return "%s-%s" % (order.id, order.order_total)
    
    def get_order_unique_id(self, order):
        '''
        A unique identifier for this order. This should be our shop's reference 
        number. This is sent back by the payment processor when confirming 
        payment, for example.
        '''
        return order.id
    
    def get_order_for_id(self, id):
        '''
        Get an order for a given ID. Typically, this would be used when the backend
        receives notification from the transaction processor (i.e. paypal ipn),
        with an attached "invoice ID" or "order ID", which should then be used to 
        get the shop's order with this method.
        '''
        return Order.objects.get(pk=id)
        
#===============================================================================
# URLS
#===============================================================================
    def get_finished_url(self):
        '''
        A helper for backends, so that they can call this when their job
        is finished i.e. The payment has been processed from a user perspective
        This will redirect to the "Thanks for your order" page.
        '''
        return HttpResponseRedirect('thank_you_for_your_order')
    
    def get_cancel_url(self):
        return HttpResponseRedirect('checkout_payment')
