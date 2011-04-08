# django_shop/checkout/__init__.py
# django_shop/checkout/__init__.py


from django_shop.checkout.site import CheckoutSite, checkoutsite

def autodiscover():
    """
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        for submod in ('django_shop_payment', 'django_shop_shipment')
            # Attempt to import the app's admin module.
            try:
                before_import_registry = copy.copy(checkoutsite._registry)
                import_module('%s.%s' % (app, submod))
            except:
                # Reset the model registry to the state before the last import as
                # this import will have to reoccur on the next request and this
                # could raise NotRegistered and AlreadyRegistered exceptions
                # (see #8245).
                site._registry = before_import_registry
    
                # Decide whether to bubble up this error. If the app just
                # doesn't have an admin module, we can ignore the error
                # attempting to import it, otherwise we want it to bubble up.
                if module_has_submodule(mod, submod):
                    raise

# django_shop/checkout/site.py

from djangoshop.payment_base import PaymentBase
from djangoshop.shipper_base import ShipperBase

from django.views.generic import TemplateView

class CheckoutView(TemplateView):
    template_name = "checkout.html"

class CheckoutSite(object):

    checkout_view = CheckoutView.as_view()
    
    def __init__(self, name=None, app_name='django_shop'):
        self._registry = {
            'shipper': {},
            'payment': {}
        }
         # model_class class -> admin_class instance
        self.root_path = None
        if name is None:
            self.name = 'checkout'
        else:
            self.name = name
        self.app_name = app_name
        
    def register(self, registry, classtype, class_or_iterable):
        """
        Registers the given model(s) with the checkoutsite
        """
        if isinstance(cls, classtype):
            class_or_iterable = [class_or_iterable]
        for cls in class_or_iterable:
            if cls in self._registry[registry].keys():
                raise AlreadyRegistered('The %s class %s is already registered' % (registry, cls.__name__))
            # Instantiate the class to save in the registry
            self._registry[registry][cls] = cls(self)

     def unregister(self, registry, classtype, class_or_iterable):
        """
        Unregisters the given classes(s).

        If a class isn't already registered, this will raise NotRegistered.
        """
        if isinstance(cls, classtype):
            class_or_iterable = [class_or_iterable]
        for cls in class_or_iterable:
            if cls not in self._registry[registry].keys():
                raise NotRegistered('The %s class %s is not registered' % (registry, cls.__name__))
            del self._registry[registry][cls] 
            
    def register_shipper(self, shipper):
        self.register(self, 'shipper', ShipperBase, shipper)
            
    def unregister_shipper(self, shipper):
        self.unregister(self, 'shipper', ShipperBase, shipper)
        
    def register_payment(self, payment):
        self.register(self, 'payment', PaymentBase, payment)
            
    def unregister_payment(self, payment):
        self.unregister(self, 'payment', PaymentBase, payment)
                
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
                    url(r'^payment/%s/' % payment.url_prefix,
                        include(shipper.urls))
                )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

checkoutsite = CheckoutSite()

# django_shop/checkout/shipper_base.py

class ShipperBase(object)
    pass
    
# django_shop/checkout/payment_base.py
from djangoshop. import RegisterAbleClass

class PaymentBase(object)

  def __init__(self, checkout_site):
    self.checkout_site = checkout_site
    super(PaymentBase, self).__init__()
    
# app/django_shop_shipment.py

from djangoshop.shipper_base import ShipperBase

class ShipmentClass(ShipperBase):

  def __init__(self, checkout_site):
    self.checkout_site = checkout_site
    super(PaymentBase, self).__init__()
    
checkoutsite.register_shipment(ShipmentClass)

# app/django_shop_payment.py

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
                name='%s_payment' % self.url_prefix),
        )
        return urlpatterns
        
    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
checkoutsite.register_payment(PaymentClass)
