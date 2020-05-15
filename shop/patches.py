from cms.models import Page
from cms.templatetags.cms_tags import PageAttribute as BrokenPageAttribute


class PageAttribute(BrokenPageAttribute):
    """
    This monkey patch can be withdrawn, after https://github.com/divio/django-cms/issues/5930
    has been fixed.
    """
    def get_value_for_context(self, context, **kwargs):
        try:
            return super().get_value_for_context(context, **kwargs)
        except Page.DoesNotExist:
            return ''
