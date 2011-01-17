'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from payment.payment_backend_base import BasePaymentBackend

class PayOnDeliveryBackend(BasePaymentBackend):
    
    def process_order(self,order):
        '''
        Pseudocode, I'm sure you'll get the idea
        
        for item in order:
            email_text.append("%s %s %s" % (item.name, item.quantity, item.price))
        email_text.append("    %s" % (order.total))
        '''