# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template import RequestContext
from rest_framework import renderers


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

        if response.exception:
            template = self.get_exception_template(response)
        else:
            view = context['view']
            template_names = self.get_template_names(response, view)
            template = self.resolve_template(template_names)
            context['paginator'] = view.paginator
            # set edit_mode, so that otherwise invisible placeholders can be edited inline
            context['edit_mode'] = request.current_page.publisher_is_draft
        try:
            # DRF >= 3.4.2
            template_context = self.get_template_context(context, context)
        except AttributeError:
            # Fallback for DRF < 3.4.2
            template_context = self.resolve_context({}, request, response)
        template_context['data'] = data
        return template.render(template_context, request=request)
