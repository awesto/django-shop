# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import renderers
from rest_framework.compat import template_render

from shop.models.cart import CartModel
from shop.serializers.cart import CartSerializer


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

        if response.exception:
            template = self.get_exception_template(response)
        else:
            template_names = self.get_template_names(response, view)
            template = self.resolve_template(template_names)
            template_context['paginator'] = view.paginator
            # set edit_mode, so that otherwise invisible placeholders can be edited inline
            template_context['edit_mode'] = getattr(request.current_page, 'publisher_is_draft', False)

        template_context['data'] = data
        template_context.update(renderer_context)
        return template_render(template, template_context, request=request)


class CatalogRenderer(renderers.TemplateHTMLRenderer):
    """
    Modified TemplateHTMLRenderer, which can be used to render the templates used in the catalog
    view.
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

        template_context['data'] = data
        self.update_with_cart_context(context)
        template_context.update(context)
        return template.render(template_context, request=request)

    def update_with_cart_context(self, context):
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            context['is_cart_filled'] = cart.items.exists()
            cart_serializer = CartSerializer(cart, context=context, label='cart')
            context['cart'] = cart_serializer.data
        except (KeyError, CartModel.DoesNotExist):
            pass
