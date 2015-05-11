# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class AuthFormsView(GenericAPIView):
    serializer_class = None
    form_class = None

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.DATA, instance=request.user)
        if form.is_valid():
            form.save(request=request)
            return Response(form.data, status=status.HTTP_200_OK)
        return Response(dict(form.errors), status=status.HTTP_400_BAD_REQUEST)
