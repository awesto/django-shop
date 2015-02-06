# -*- coding: utf-8 -*-
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from shop.models.cart import BaseProduct


class BaseProductSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    #price = serializers.CharField(source='get_price', read_only=True)

    class Meta:
        model = getattr(BaseProduct, 'MaterializedModel')
        fields = ('url',) + model.serialize_fields


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view(['GET', 'POST'])
def product_list(request, format=None):
    ProductModel = getattr(BaseProduct, 'MaterializedModel')
    if request.method == 'GET':
        products = ProductModel.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def product_detail(request, pk, format=None):
    ProductModel = getattr(BaseProduct, 'MaterializedModel')
    try:
        product = ProductModel.objects.get(pk=pk)
    except ProductModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
