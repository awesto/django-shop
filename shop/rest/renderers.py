# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from collections import OrderedDict
from rest_framework import renderers
from shop import app_settings


class CMSPageRenderer(renderers.TemplateHTMLRenderer):
    """
    Modified TemplateHTMLRenderer, which is able to render CMS pages containing the templatetag
    `{% render_placeholder ... %}`, and which accept ordinary Python objects in their rendering
    context.
    The serialized data object, as available to other REST renderers, is explicitly added to the
    context as ``data``. Therefore keep in mind that templates for REST's `TemplateHTMLRenderer`
    are not compatible with this renderer.
    """
    def render(self, data, accepted_media_type=None, context=None):
        request = context['request']
        response = context['response']
        template_context = {}

        if response.exception:
            template = self.get_exception_template(response)
        else:
            view = context['view']
            template_names = self.get_template_names(response, view)
            template = self.resolve_template(template_names)
            template_context['paginator'] = view.paginator
            # set edit_mode, so that otherwise invisible placeholders can be edited inline
            template_context['edit_mode'] = request.current_page.publisher_is_draft

        template_context['data'] = data
        # To keep compatibility with previous versions, we copy the renderer context to the template
        # context. Maybe it would be a good idea to not do this, to force templates to use the
        # serialized data.
        template_context.update(context)
        return template.render(template_context, request=request)


class DashboardRenderer(renderers.TemplateHTMLRenderer):
    """
    Modified TemplateHTMLRenderer, which is used to add render the dashboard.
    """
    def get_template_names(self, response, view):
        app_label = app_settings.APP_LABEL
        if view.action == 'list':
            template_names = [
                os.path.join(app_label, 'dashboard/list-view.html'),
                'shop/dashboard/list-view.html',
            ]
        elif view.action == 'retrieve':
            obj = view.get_object()
            template_names = [
                os.path.join(app_label, 'dashboard/{}-detail-view.html'.format(obj.product_model)),
                os.path.join(app_label, 'dashboard/detail-view.html'),
                'shop/dashboard/detail-view.html',
            ]
        elif view.action == 'create':
            template_names = []
        else:
            msg = "Action '{}' is now declared for rendering the dashboard"
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
        serializer = view.list_serializer_class()
        list_display_fields = OrderedDict()
        for field_name in view.get_list_display():
            list_display_fields[field_name] = serializer.fields[field_name]
        data['list_display_fields'] = list_display_fields
        data['list_display_links'] = view.get_list_display_links()
        return data
