# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag
from cms.plugin_rendering import ContentRenderer
from cms.models.placeholdermodel import Placeholder
#from cms.templatetags.cms_tags import RenderPlaceholder
from django import template
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.utils.html import strip_tags
from django.utils.six import string_types
from sekizai.context_processors import sekizai

register = template.Library()


class EmulateHttpRequest(HttpRequest):
    """
    Use this class to emulate a HttpRequest object.
    """
    def __init__(self, language_code=None):
        super(EmulateHttpRequest, self).__init__()
        self.environ = {}
        self.method = 'GET'
        if language_code:
            self.LANGUAGE_CODE = language_code
        self.user = AnonymousUser()
        self.current_page = None


class RenderPlaceholder(AsTag):
    """
    Modified templatetag render_placeholder to be used for rendering the search index templates.
    """
    name = 'render_placeholder'
    options = Options(
        Argument('placeholder'),
        Argument('width', default=None, required=False),
        'language',
        Argument('language', default=None, required=False),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def _get_value(self, context, editable=True, **kwargs):
        renderer = ContentRenderer(context['request'])
        placeholder = kwargs.get('placeholder')
        if not placeholder:
            return ''
        if isinstance(placeholder, string_types):
            placeholder = Placeholder.objects.get(slot=placeholder)
        content = renderer.render_placeholder(
            placeholder=placeholder,
            context=context,
            language=kwargs.get('language'),
            editable=editable,
            use_cache=False,
            width=kwargs.get('width'),
        )
        return strip_tags(content).replace('\n', '').replace('\t', '')

    def get_value_for_context(self, context, **kwargs):
        return self._get_value(context, editable=False, **kwargs)

    def get_value(self, context, **kwargs):
        try:
            language_code = context['object']._current_language
        except (KeyError, AttributeError):
            language_code = None
        context['request'] = EmulateHttpRequest(language_code)
        context.update(sekizai())
        return self._get_value(context, **kwargs)

register.tag('render_placeholder', RenderPlaceholder)
