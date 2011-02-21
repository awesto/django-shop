# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from shop.models.ordermodel import OrderItem, ExtraOrderItemPriceField, \
    ExtraOrderPriceField


class PayOnDeliveryBackend(object):
    
    backend_name = "Pay On Delivery"
    url_namespace = "pay-on-delivery"
    
    def __init__(self, shop):
        self.shop = shop # This is the shop reference, it allows this backend
        # to interact with it in a tidy way (look ma', no imports!)
    
    def _create_body(self, order):
        '''
        A drill to put all of the Order's content as text... little
        attempt at beautifying was made so far
        '''
        if order == None:
            return "" # Don't waste your time here.
        
        email_body = []
        email_body.append("A new order was placed!")
        email_body.append("")
        
        order_items = OrderItem.objects.filter(order=order)
        
        for item in order_items:
            line = ""
            line = line + ('Ref: %s| ' % item.product_reference )
            line = line + ('Name: %s| ' % item.product_name )
            line = line + ('Price: %s| ' % item.unit_price )
            line = line + ('Q: %s| ' % item.quantity )
            line = line + ('SubTot: %s| ' % item.line_subtotal )
            extra = ExtraOrderItemPriceField.objects.filter(order_item=item)
            for x in extra:
                line = line + ("%s: %s|" % (x.label,x.value))
            line = line + ('Tot: %s| ' % item.line_total )
            email_body.append(line)
            
        email_body.append("")
        email_body.append("Subtotal: %s" % order.order_subtotal)
        extra = ExtraOrderPriceField.objects.filter(order=order)
        for x in extra:
            email_body.append("%s: %s" % (x.label,x.value))
        email_body.append("Total: %s" % order.order_total)
        email_body = "\n".join(email_body)
        return email_body
            
    def simple_view(self, request):
        # Get the order object
        the_order = self.shop.getOrder(request)
        # Set the payment method to be this backend (for traceability)
        self.shop.set_payment_method(the_order, self.backend_name)
        # Set it as payed (it needs to be payed to the delivery guy, we assume 
        # he does his job properly)
        self.shop.pay(the_order, the_order.order_total)
        # TODO: Needs a better view than this!
        return HttpResponse('%s' % self._create_body(the_order))
        
    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.simple_view, name='pay-on-delivery' ),
        )
        return urlpatterns
    