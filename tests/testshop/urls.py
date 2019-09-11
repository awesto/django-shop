from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION < (2, 0):
    from django.conf.urls import url, include
else:
    from django.urls import include, path, re_path
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

if DJANGO_VERSION < (2, 0):
    urlpatterns = [
        url(r'^shop/', include('shop.urls', namespace='shop')),
    ]
    urlpatterns.extend(i18n_patterns(
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('cms.urls')),
    ))
else:
    urlpatterns = [
        path('shop/', include(('shop.urls', 'shop_urls' ), namespace='shop')),
    ]
    urlpatterns.extend(i18n_patterns(
        path('admin/', admin.site.urls),
        path('', include('cms.urls')),
    ))
