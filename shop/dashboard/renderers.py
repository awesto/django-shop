# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from rest_framework import renderers

from shop import app_settings


class DashboardRenderer(renderers.TemplateHTMLRenderer):
    """
    Modified TemplateHTMLRenderer, which is used to add render the dashboard.
    """
    def get_template_names(self, response, view):
        app_label = app_settings.APP_LABEL
        if view.suffix == 'List':
            template_names = [
                os.path.join(app_label, 'dashboard/list-view.html'),
                'shop/dashboard/list-view.html',
            ]
        elif view.suffix == 'Instance':
            obj = view.get_object()
            template_names = [
                os.path.join(app_label, 'dashboard/{}-change-view.html'.format(obj._meta.model_name)),
                os.path.join(app_label, 'dashboard/change-view.html'),
                'shop/dashboard/change-view.html',
            ]
        elif view.suffix == 'New':
            template_names = [
                os.path.join(app_label, 'dashboard/change-view.html'),
                'shop/dashboard/change-view.html',
            ]
        else:
            msg = "The given route for '{}' must be declared for rendering the dashboard"
            raise NotImplementedError(msg.format(view.action))
        return template_names

    def get_template_context(self, data, renderer_context):
        view = renderer_context['view']
        response = renderer_context['response']
        if response.exception:
            data['status_code'] = response.status_code

        # erich the context with data from the model
        options = view.list_serializer_class.Meta.model._meta
        data['model_options'] = options
        data.update(renderer_context['template_context'])

        return data
