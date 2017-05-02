# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict, namedtuple

from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from rest_framework import fields, relations, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from shop import app_settings
from shop.models.product import ProductModel
from shop.money.serializers import JSONEncoder
from shop.rest.money import JSONRenderer
from shop.rest.fields import AmountField
from shop.serializers.bases import ProductSerializer


NgField = namedtuple('NgField', ['field_type', 'serializers', 'extra_bits', 'template_context'])


class DashboardPaginator(PageNumberPagination):
    page_size = 20
    page_query_param = '_page'
    page_size_query_param = '_perPage'


class ProductsDashboard(ModelViewSet):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    pagination_class = DashboardPaginator
    list_serializer_class = None
    detail_serializer_classes = {}
    #permission_classes = [IsAuthenticated]
    queryset = ProductModel.objects.all()

    def get_serializer_class(self):
        if self.suffix == 'List':
            return self.list_serializer_class
        elif self.suffix == 'Instance':
            instance = self.get_object()
            return self.detail_serializer_classes.get(instance._meta.label_lower, ProductSerializer)
        msg = "ViewSet 'ProductsDashboard' is not implemented for suffix '{}'"
        raise NotImplementedError(msg.format(self.suffix))

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        kwargs.update(context=context, label='dashboard')
        serializer = serializer_class(*args, **kwargs)
        return serializer

    @cached_property
    def list_fields(self):
        serializer = self.list_serializer_class()
        field_names = getattr(self, 'list_display', serializer.get_fields().keys())
        detail_links = getattr(self, 'list_display_links', [field_names[0]])

        list_fields = []
        for name, field in serializer.get_fields().items():
            field_type = field.style.get('field_type', 'string')
            bits = ['field("{}", "{}")'.format(name, field_type)]
            if name in detail_links:
                bits.append('isDetailLink(true)')
            list_fields.append(mark_safe('.'.join(bits)))

        return list_fields

    @property
    def creation_fields(self):
        template = Template("""template(function(entry) {
            {% spaceless %}
            {% for ctype in ctypes %}
            return '<{{ field_tag }} ng-if="entry.values.polymorphic_ctype=={{ ctype.id }}" field="::field" value="entry.values[field.name()]" entry="entry" entity="::entity" form="formController.form" datastore="::formController.dataStore"></{{ field_tag }}>';
            {% endfor %}
            {% endspaceless %}
        }, {{ include_label }})""")
        choices = []
        for serializer_class in self.detail_serializer_classes.values():
            choices.append({
                'value': ContentType.objects.get_for_model(serializer_class.Meta.model).id,
                'label': serializer_class.Meta.model._meta.verbose_name,
            })
        pt_field = 'field("polymorphic_ctype", "choice").label("{}").choices({})'
        fields = [mark_safe(pt_field.format(_("Product Type"), json.dumps(choices, cls=JSONEncoder)))]
        fields.extend(self.get_detail_fields(template))
        return fields

    #@cached_property
    @property
    def edition_fields(self):
        template = Template("""template(function(entry) {
            {% spaceless %}{% with tag="ma-string-column" %}
            {% for ctype in ctypes %}
            if (entry.values.polymorphic_ctype == {{ ctype.id }})
                return '<{{ field_tag }} field="::field" value="entry.values[field.name()]" entry="entry" entity="::entity" form="formController.form" datastore="::formController.dataStore"></{{ field_tag }}>';
            {% endfor %}
            {% endwith %}{% endspaceless %}
        }, {{ include_label }})""")
        return self.get_detail_fields(template)

    def get_detail_fields(self, template):
        detail_fields = OrderedDict()
        for serializer_id, serializer_class in enumerate(self.detail_serializer_classes.values()):
            for name, field in serializer_class().get_fields().items():
                if field.read_only:
                    continue
                field_type, extra_bits, template_context = self.get_field_context(field)
                if name in detail_fields:
                    if detail_fields[name].field_type != field_type:
                        ng_field = NgField(field_type, [serializer_class], extra_bits, template_context)
                        detail_fields[name + str(serializer_id)] = ng_field
                    else:
                        detail_fields[name].serializers.append(serializer_class)
                else:
                    detail_fields[name] = NgField(field_type, [serializer_class], extra_bits, template_context)

        result_list = []
        for key, ng_field in detail_fields.items():
            bits = ['field("{}", "{}")'.format(key, ng_field.field_type)] + ng_field.extra_bits
            if len(ng_field.serializers) < len(self.detail_serializer_classes):
                # this field it not available for all serializer classes, handle polymorphism using
                # a template to hide the field conditionally depending on the model's content type
                ctypes = [ContentType.objects.get_for_model(sc.Meta.model) for sc in ng_field.serializers]
                render_context = Context(dict(ng_field.template_context, ctypes=ctypes))
                bits.append(template.render(render_context))
            result_list.append(mark_safe('.'.join(bits)))

        return result_list

    def get_field_context(self, field):
        """
        Method used to map Django's Field class to the field type used by ng-admin
        """
        extra_bits = ['validation({})'.format(json.dumps({'required': field.required}))]
        context = {'field_tag': 'ma-field', 'include_label': 'true'}
        if field.label is not None:
            extra_bits.append('label("{}")'.format(field.label))

        if isinstance(field, fields.BooleanField):
            field_type = 'boolean'
        elif isinstance(field, fields.IntegerField):
            field_type = 'number'
        elif isinstance(field, AmountField):
            field_type = 'float'
            #extra_bits.append('format("$0,000.00")')
            #context.update(field_tag='ma-number-column', include_label='false')
        elif isinstance(field, fields.FloatField):
            field_type = 'float'
        elif isinstance(field, fields.EmailField):
            field_type = 'email'
        elif isinstance(field, (fields.ChoiceField, relations.PrimaryKeyRelatedField)):
            field_type = 'choice'
            choices = [{'value': value, 'label': label} for value, label in field.choices.items()]
            extra_bits.append('choices({})'.format(json.dumps(choices, cls=JSONEncoder)))
        elif isinstance(field, serializers.ListSerializer):
            field_type = 'embedded_list'
            extra_bits.append('targetFields([nga.field("unit_price"), nga.field("product_code"), nga.field("storage")])')
        else:
            field_type = 'string'

        return field_type, extra_bits, context

    def has_add_permission(self):
        """
        Returns True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        codename = get_permission_codename('add', ProductModel._meta)
        return self.request.user.has_perm('{}.{}'.format(app_settings.APP_LABEL, codename))

    def list(self, request, *args, **kwargs):
        response = super(ProductsDashboard, self).list(request, *args, **kwargs)
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('dashboard:product-list')
        return Response({'serializer': serializer})

    def retrieve(self, request, *args, **kwargs):
        response = super(ProductsDashboard, self).retrieve(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        response = super(ProductsDashboard, self).update(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super(ProductsDashboard, self).destroy(request, *args, **kwargs)
        return response
