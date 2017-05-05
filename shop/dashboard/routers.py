# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, Route, DynamicDetailRoute
from rest_framework.views import APIView


class DashboardRouter(DefaultRouter):
    root_view_name = 'root'
    root_template_name = 'shop/dashboard/root.html'

    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}/change{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'update',
            },
            name='{basename}-change',
            initkwargs={'suffix': 'Instance'}
        ),
        Route(
            url=r'^{prefix}/add{trailing_slash}$',
            mapping={
                'get': 'new',
                'post': 'create',
            },
            name='{basename}-add',
            initkwargs={'suffix': 'New'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    @classmethod
    def get_breadcrumbs(cls):
        return [(_("Dashboard"), reverse('dashboard:root'))]

    def get_api_root_view(self, api_urls=None):
        dashboard_entities = OrderedDict()
        for prefix, viewset, basename in self.registry:
            dashboard_entities[prefix] = viewset()

        class RootView(APIView):
            """
            View to handle to root dashboard page.
            """
            renderer_classes = (TemplateHTMLRenderer,)

            def get(self, request, *args, **kwargs):
                context = {
                    'breadcrumblist': DashboardRouter.get_breadcrumbs()
                }
                return Response(context, template_name=DashboardRouter.root_template_name)

        return RootView.as_view()
