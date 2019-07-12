from django.urls import include, path, re_path
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

urlpatterns = [
    path('shop/', include('shop.urls', namespace='shop')),
]
urlpatterns.extend(i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('cms.urls')),
))
