# djangoshop/checkout.py
from django.views.generic import TemplateView

class CheckoutView(TemplateView):
    template_name = "checkout.html"

class CheckoutSite(object):

    checkout_view = CheckoutView.as_view()
    
    def __init__(self, name=None, app_name='django_shop'):
        self._payment_registry = []
        self._shippers_registry = []
         # model_class class -> admin_class instance
        self.root_path = None
        if name is None:
            self.name = 'checkout'
        else:
            self.name = name
        self.app_name = app_name
        
    def register(self, registry, class_or_iterable):
        """
        Registers the given model(s) with the checkoutsite
        """
            
        if isinstance(cls, ShipperBase) or isinstance(cls, PaymentBase):
            class_or_iterable = [class_or_iterable]
        for cls in class_or_iterable:
            if cls in getattr(self, '_%s_registry' % registry):
                raise AlreadyRegistered('The class %s is already registered' % model.__name__)
            # Instantiate the class to save in the registry
            getattr(self, '_%s_registry' % registry).append(cls(self))

    def unregister(self, model_or_iterable):
        """
        Unregisters the given model(s).

        If a class isn't already registered, this will raise NotRegistered.
        """
        if isinstance(cls, ShipperBase) or isinstance(cls, PaymentBase):
            class_or_iterable = [class_or_iterable]
        for cls in class_or_iterable:
            if cls in getattr(self, '_%s_registry' % registry):
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]
                    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        # Checkout-site-wide views.
        urlpatterns = patterns('',
            url(r'^$', self.checkout_view, name='checkout'),
        )

        # Add in each model's views.
        for payment in self._payment_registry:
            if hasattr(payment, 'urls'):
                urlpatterns += patterns('',
                    url(r'^shipment/%s/%s/' % payment.url_prefix,
                        include(payment.urls))
                )
        for shipper in self._shippers_registry:
            if hasattr(shipper, 'urls'):
                urlpatterns += patterns('',
                    url(r'^payment/%s/ % payment.url_prefix,
                        include(shipper.urls))
                )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

def autodiscover():
    pass

# djangoshop/__init__.py

from djangoshop.checkout import CheckoutSite
checkoutsite = CheckoutSite()

# djangoshop/shipper_base.py

class ShipperBase(object)
    pass
    
# djangoshop/payment_base.py
from djangoshop. import RegisterAbleClass

class PaymentBase(object)

  def __init__(self, checkout_site):
    self.checkout_site = checkout_site
    super(PaymentBase, self).__init__()
    
# app/djangoshop_shipper.py

from djangoshop.shipper_base import ShipperBase

class ShipmentClass(ShipperBase):

  def __init__(self, checkout_site):
    self.checkout_site = checkout_site
    super(PaymentBase, self).__init__()
    
checkoutsite.register_shipment(ShipmentClass)

# app/djangoshop_payment.py

from django.views.generic import TemplateView
from djangoshop.payment_base import PaymentBase

class PaymentView(TemplateView):
    template_name = "payment.html"

class PaymentClass(PaymentBase, UrlMixin):
    
    url_prefix = 'payment'
    
    payment_view = PaymentView.as_view()
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'^$', self.payment_view,
                name='%s_payment' % self.url_prefix,
        )
        return urlpatterns
        
    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
checkoutsite.register_payment(PaymentClass)
