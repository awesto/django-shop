# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework import views
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response


class FileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)
    storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'dashboard'),
                                base_url=settings.MEDIA_URL + 'dashboard')

    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        available_name = self.storage.get_available_name(file_obj.name)
        self.storage.save(available_name, file_obj)
        data = {'filename': available_name, 'url': self.storage.url(available_name)}
        return Response(data=data)
