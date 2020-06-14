from cms.plugin_rendering import ContentRenderer
from cms.models.placeholdermodel import Placeholder
from cms.templatetags.cms_tags import RenderPlaceholder as DefaultRenderPlaceholder
from django import template
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.utils.html import strip_tags
from sekizai.context_processors import sekizai

register = template.Library()


class EmulateHttpRequest(HttpRequest):
    """
    Use this class to emulate a HttpRequest object.
    """
    def __init__(self, language_code=None):
        super().__init__()
        self.environ = {}
        self.method = 'GET'
        if language_code:
            self.LANGUAGE_CODE = language_code
        self.user = AnonymousUser()
        self.current_page = None


class RenderPlaceholder(DefaultRenderPlaceholder):
    """
    Modified templatetag render_placeholder to be used for rendering the search index templates.
    """
    def _get_value(self, context, editable=True, **kwargs):
        renderer = ContentRenderer(context['request'])
        placeholder = kwargs.get('placeholder')
        if not placeholder:
            return ''
        if isinstance(placeholder, str):
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

    def get_value(self, context, **kwargs):
        context.update(sekizai())
        try:
            language_code = context['product']._current_language
        except (KeyError, AttributeError):
            language_code = None
        context['request'] = EmulateHttpRequest(language_code)
        return self._get_value(context, **kwargs)

register.tag('render_placeholder', RenderPlaceholder)
