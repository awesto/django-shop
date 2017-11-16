# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import os

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.exceptions import TemplateDoesNotExist

register = template.Library()


@register.simple_tag
def raw_include(path):
    filename = os.path.join(settings.DOCS_ROOT, path)
    if not os.path.exists(filename):
        raise TemplateDoesNotExist("'{path}' does not exist".format(path=path))
    with io.open(filename) as fh:
        return mark_safe(fh.read())
