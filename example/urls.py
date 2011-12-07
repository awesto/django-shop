from django.conf.urls.defaults import *
from shop.views import ShopTemplateView

from shop import urls as shop_urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^shop_example/', include('shop_example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    #Home
    url(r'^$', ShopTemplateView.as_view(template_name="shop/welcome.html"),
        name='shop_welcome'),

    (r'^', include(shop_urls)), # <-- That's the important bit
)
