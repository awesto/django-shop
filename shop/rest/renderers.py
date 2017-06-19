# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context

from rest_framework import renderers
from rest_framework.compat import template_render
from rest_framework.exceptions import APIException

from shop.models.cart import CartModel
from shop.serializers.cart import CartSerializer


class ShopTemplateHTMLRenderer(renderers.TemplateHTMLRenderer):
    """
    Modified TemplateHTMLRenderer, which shall be used to render templates used by django-SHOP.
    Instead of polluting the template context with the serialized data, that information is
    stored inside a separate `data` attribute, which allows to add a Cart and Paginator object.

    Templates created for this renderer are compatible with the `CMSPageRenderer` (see below).
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context['request']
        response = renderer_context['response']

        if response.exception:
            template = self.get_exception_template(response)
            template_context = Context(self.get_template_context(data, renderer_context))
            return template.render(template_context)

        view = renderer_context['view']
        template_names = self.get_template_names(response, view)
        template = self.resolve_template(template_names)
        template_context = {
            'paginator': view.paginator,
            'data': data,
        }
        self.update_with_cart_context(renderer_context)
        template_context.update(renderer_context)
        return template.render(template_context, request=request)

    def update_with_cart_context(self, context):
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            context['is_cart_filled'] = cart.items.exists()
            cart_serializer = CartSerializer(cart, context=context, label='cart')
            context['cart'] = cart_serializer.data
        except (KeyError, CartModel.DoesNotExist):
            pass


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

        if not getattr(request, 'current_page', None):
            msg = "APIView class '{}' with 'renderer_class=(CMSPageRenderer, ...)' can only be used by a CMSApp"
            response = view.handle_exception(APIException(detail=msg.format(view.__class__)))

        if response.exception:
            template = self.get_exception_template(response)
            template_context = Context(self.get_template_context(data, renderer_context))
            return template.render(template_context)

        template_names = [request.current_page.get_template()]
        template = self.resolve_template(template_names)
        template_context = self.get_template_context(dict(data), renderer_context)
        template_context.update(
            renderer_context,
            paginator=view.paginator,
            # set edit_mode, so that otherwise invisible placeholders can be edited inline
            edit_mode=getattr(request.current_page, 'publisher_is_draft', False),
            data=data,
        )
        return template_render(template, template_context, request=request)
