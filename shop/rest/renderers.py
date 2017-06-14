# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import renderers
from rest_framework.compat import template_render
from rest_framework.exceptions import APIException


class CMSPageRenderer(renderers.TemplateHTMLRenderer):
    """
    Modified TemplateHTMLRenderer, which is able to render CMS pages containing the templatetag
    `{% render_placeholder ... %}`, and which accept ordinary Python objects in their rendering
    context.
    The serialized data object, as available to other REST renderers, is explicitly added to the
    context as ``data``. Therefore keep in mind that templates for REST's `TemplateHTMLRenderer`
    are not compatible with this renderer.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']
        template_context = self.get_template_context(dict(data), renderer_context)

        if not getattr(request, 'current_page', None):
            msg = "APIView class '{}' with 'renderer_class=(CMSPageRenderer, ...)' can only be used by a CMSApp"
            response = view.handle_exception(APIException(detail=msg.format(view.__class__)))

        if response.exception:
            template = self.get_exception_template(response)
        else:
            template_names = [request.current_page.get_template()]
            template = self.resolve_template(template_names)
            template_context['paginator'] = view.paginator
            # set edit_mode, so that otherwise invisible placeholders can be edited inline
            template_context['edit_mode'] = request.current_page.publisher_is_draft

        template_context['data'] = data
        template_context.update(renderer_context)
        return template_render(template, template_context, request=request)
