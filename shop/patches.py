# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cms.models import Page
from cms.templatetags.cms_tags import PageAttribute as BrokenPageAttribute


class PageAttribute(BrokenPageAttribute):
    def get_value_for_context(self, context, **kwargs):
        try:
            return super(PageAttribute, self).get_value_for_context(context, **kwargs)
        except Page.DoesNotExist:
            return ''
