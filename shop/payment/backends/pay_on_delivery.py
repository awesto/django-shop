# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail
from shop.models.ordermodel import OrderItem, ExtraOrderItemPriceField, \
    ExtraOrderPriceField, Order
from shop.payment.payment_backend_base import BasePaymentBackend


class PayOnDeliveryBackend(BasePaymentBackend):
    
    def _create_email_body(self, order):
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
            
    def process_order(self,order):
        '''
        This should simply save the order in the database with relevant 
        information, set the order's status to "completed", and send an
        email to the admin (it's an example plugin, obviously)
        '''
        recipients = [x[1] for x in settings.ADMINS]
        body = self._create_email_body(order)
        send_mail('New order!', body, 'shop@example.com',
                  [recipients], fail_silently=False)
        order.status = Order.COMPLETED
        order.save()
            
        
        
        
        
        