# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def mustaches(string, args):
    """
    Used to replace the part of an URL with a counterpart wrapped in mustaches.
    This is required to reuse the result of a Django's urlresolver with an interpolation
    string as required by AngularJS.

    Example:
        {% url 'detail-viewname' pk=':PK:' as detail_url %}
        {{ detail_url|mustaches:":PK:entry.pk" }}

        This would for instance render a request the URL as:
        ```
        /list/{{ entry.pk }}/detail
        ```
        which is perfectly suitable inside AngularJS ``ng-href`` directives.
    """
    search = args[0] + args.split(args[0])[1] + args[0]
    replace = '{{ ' + args.split(args[0])[2] + ' }}'
    return re.sub(search, replace, string)
