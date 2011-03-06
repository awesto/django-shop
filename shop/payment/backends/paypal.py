from datetime import datetime
from decimal import Decimal
import urllib

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

class PaypalPaymentBackend(object):
    backend_name = 'Paypal'
    url_namespace = 'paypal'

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        return patterns('',
            url(r'^/$', self.ipn, name='paypal_ipn'),
            url(r'^ipn/$', self.ipn, name='paypal_ipn'),
        )

    def process_order_confirmed(self, request):
        PAYPAL = settings.PAYPAL
        # Get the order object from the request using the shop interface
        order = self.shop.get_order(request)
        
        if self.shop.is_order_payed(order):
            if not self.shop.is_order_complete(order):
#                logger.info('Order %s is already completely paid' % order)

                self.create_transactions(order, _('sale'),
                    type=StockTransaction.SALE, negative=True)

                if order.is_paid():
                    self.order_completed(order)

            return self.shop.finished()

        #logger.info('Processing order %s using Paypal' % order)

        payment = self.create_pending_payment(order)
        
        self.create_transactions(order, _('payment process reservation'),
            type=StockTransaction.PAYMENT_PROCESS_RESERVATION,
            negative=True, payment=payment)

        if PAYPAL['LIVE']:
            PP_URL = "https://www.paypal.com/cgi-bin/webscr"
        else:
            PP_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"

        return render_to_response('payment/paypal_form.html', {
            'order': order,
            'payment': payment,
            'HTTP_HOST': request.META.get('HTTP_HOST'),
            'post_url': PP_URL,
            'business': PAYPAL['BUSINESS'],
            }, context_instance=RequestContext(request))

    def ipn(self, request):
        request.encoding = 'windows-1252'
        PAYPAL = settings.PAYPAL

        if PAYPAL['LIVE']:
            PP_URL = "https://www.paypal.com/cgi-bin/webscr"
        else:
            PP_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"

        parameters = None

        try:
            parameters = request.POST.copy()
            parameters_repr = repr(parameters).encode('utf-8')

            if parameters:
                logger.info('IPN: Processing request data %s' % parameters_repr)

                postparams = {'cmd': '_notify-validate'}
                for k, v in parameters.iteritems():
                    postparams[k] = v.encode('windows-1252')
                status = urllib.urlopen(PP_URL, urllib.urlencode(postparams)).read()

                if not status == "VERIFIED":
                    logger.error('IPN: Received status %s, could not verify parameters %s' % (
                        status, parameters_repr))
                    parameters = None

            if parameters:
                logger.info('IPN: Verified request %s' % parameters_repr)
                reference = parameters['txn_id']
                invoice_id = parameters['invoice']
                currency = parameters['mc_currency']
                amount = parameters['mc_gross']

                try:
                    order, order_id, payment_id = invoice_id.split('-')
                except ValueError:
                    logger.error('IPN: Error getting order for %s' % invoice_id)
                    return HttpResponseForbidden('Malformed order ID')

                try:
                    order = self.shop.order_model.objects.get(pk=order_id)
                except self.shop.order_model.DoesNotExist:
                    logger.error('IPN: Order %s does not exist' % order_id)
                    return HttpResponseForbidden('Order %s does not exist' % order_id)

                try:
                    payment = order.payments.get(pk=payment_id)
                except order.payments.model.DoesNotExist:
                    payment = order.payments.model(
                        order=order,
                        payment_module=u'%s' % self.name,
                        )

                payment.status = OrderPayment.PROCESSED
                payment.currency = currency
                payment.amount = Decimal(amount)
                payment.data = request.POST.copy()
                payment.transaction_id = reference
                payment.payment_method = payment.payment_module

                if parameters['payment_status'] == 'Completed':
                    payment.authorized = datetime.now()
                    payment.status = OrderPayment.AUTHORIZED

                payment.save()
                order = order.reload()

                logger.info('IPN: Successfully processed IPN request for %s' % order)

                if payment.authorized:
                    self.create_transactions(order, _('sale'),
                        type=StockTransaction.SALE, negative=True, payment=payment)

                if order.is_paid():
                    self.order_completed(order, payment=payment)

                return HttpResponse("Ok")

        except Exception, e:
            logger.error('IPN: Processing failure %s' % unicode(e))
            raise
    ipn.csrf_exempt = True
