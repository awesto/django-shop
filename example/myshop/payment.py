from django.conf.urls.defaults import patterns, url
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from shop.util.decorators import on_method, shop_login_required, order_required


class ExamplePayment(object):
    backend_name = "Example payment"
    backend_verbose_name = _("Example payment")
    url_namespace = "example-payment"

    def __init__(self, shop):
        self.shop = shop
        self.template = 'myshop/example_payment.html'

    @on_method(shop_login_required)
    @on_method(order_required)
    def show_payment(self, request):
        if request.POST:
            return self.process_payment(request)

        the_order = self.shop.get_order(request)
        ctx = {
            'order': the_order,
        }
        return render_to_response(self.template, ctx, context_instance=RequestContext(request))

    @on_method(shop_login_required)
    @on_method(order_required)
    def process_payment(self, request):
        the_order = self.shop.get_order(request)
        self.shop.confirm_payment(
            the_order, self.shop.get_order_total(the_order), "None",
            self.backend_name)
        return HttpResponseRedirect(self.shop.get_finished_url())

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.show_payment, name='example-payment'),
            url(r'^$', self.process_payment, name='process-payment'),
        )
        return urlpatterns
