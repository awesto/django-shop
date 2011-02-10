#-*- coding: utf-8 -*-

'''
Loop over payment backends defined in settings.SOMETHING and add their urls
to the payment namespace. eg:
http://www.example.com/shop/pay/paypal
http://www.example.com/shop/pay/pay-on-delivery
...
'''
from django.conf.urls.defaults import patterns
from shop.payment.payment_backend_pool import payment_backends_pool

urlpatterns = patterns('')

for backend in payment_backends_pool.get_backends_list():
    urlpatterns = backend.get_urls() + urlpatterns
