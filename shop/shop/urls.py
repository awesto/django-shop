from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


# from django.conf.urls import url
# from rest_framework_swagger.views import get_swagger_view
#
# schema_view = get_swagger_view(title='Pastebin API')
#
# urlpatterns = [
#     url(r'^$', schema_view)
# ]

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Shop",
#         default_version="v1",
#         description="Django Shop",
#         terms_of_service="",
#         contact=openapi.Contact(email="info@blarebit.com"),
#         license=openapi.License(name=""),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    url(r'^shop/', include('shop.shopurls', namespace='shop')),

    # Swagger.
    # path(
    #     "swagger/",
    #     schema_view.with_ui("swagger", cache_timeout=0),
    #     name="schema-swagger-ui",
    # ),
]
urlpatterns.extend(i18n_patterns(
    url(r'^admin/', admin.site.urls),
    # url(r'^swagger/', schema_view),
    # url(r'^', include('cms.urls')),
))
