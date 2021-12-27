from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

urlpatterns = [
    url(r'^shop/', include('shop.urls', namespace='shop')),
]
urlpatterns.extend(i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^', include('cms.urls')),
))
