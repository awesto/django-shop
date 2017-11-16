# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import mimetypes
import os

from django.conf import settings
from django.core.exceptions import ViewDoesNotExist
from django.http.response import HttpResponse
from django.views.generic import TemplateView
from django.utils.cache import patch_cache_control
from django.utils.safestring import mark_safe


class DocumentationView(TemplateView):
    template_name = 'myshop/pages/documentation.html'

    def get(self, request, *args, **kwargs):
        page = kwargs.get('page', '')
        _, extension = os.path.splitext(page)
        if extension in ['.png', '.jpg', '.jpeg', '.gif']:
            filename = os.path.join(settings.DOCS_ROOT, page)
            content_type, _ = mimetypes.guess_type(filename)
            with io.open(filename, 'rb') as fd:
                response = HttpResponse(content=fd.read(), content_type=content_type)
                patch_cache_control(response, cache_control='max-age=86400')
                return response
        return super(DocumentationView, self).get(request, *args, **kwargs)

    def get_context_data(self, page='index.html', **kwargs):
        context = super(DocumentationView, self).get_context_data(**kwargs)
        filename = os.path.join(settings.DOCS_ROOT, page, 'index.html')
        if not os.path.exists(filename):
            raise ViewDoesNotExist("{} does not exist".format(page))
        with io.open(filename, encoding='utf-8') as fd:
            context.update(page_content=mark_safe(fd.read()))
        return context
