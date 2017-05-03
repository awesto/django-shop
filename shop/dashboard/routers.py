# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView


class DashboardRouter(DefaultRouter):
    root_view_name = 'root'

    def get_api_root_view(self, api_urls=None):
        dashboard_entities = OrderedDict()
        for prefix, viewset, basename in self.registry:
            dashboard_entities[prefix] = viewset()

        class RootView(APIView):
            """
            View to handle to root dashboard page.
            """
            renderer_classes = (TemplateHTMLRenderer,)
            template_name = 'shop/dashboard/main.html'

            def get(self, request, *args, **kwargs):
                context = {
                    'dashboard_entities': dashboard_entities,
                }
                return Response(context, template_name=self.template_name)

        return RootView.as_view()
