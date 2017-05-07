# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict, namedtuple
from decimal import Decimal

from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from rest_framework import fields, relations, serializers
from rest_framework.exceptions import APIException
from rest_framework.fields import empty
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.viewsets import ModelViewSet

from shop import app_settings
from shop.models.product import ProductModel
from shop.money.serializers import JSONEncoder
from shop.rest.money import JSONRenderer
from shop.dashboard.fields import TextField
from shop.dashboard.serializers import ProductListSerializer, ProductDetailSerializer


NgField = namedtuple('NgField', ['field_type', 'serializers', 'extra_bits', 'template_context'])


class DashboardPaginator(PageNumberPagination):
    page_size = 20
    page_query_param = '_page'
    page_size_query_param = '_perPage'


class HiddenDashboardField(APIException):
    pass


class DashboardViewSet(ModelViewSet):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    pagination_class = DashboardPaginator
    list_serializer_class = ProductListSerializer
    detail_serializer_classes = {}  # for polymorphic products
    detail_serializer_class = ProductDetailSerializer  # for uniform products
    #permission_classes = [IsAuthenticated]
    queryset = ProductModel.objects.all()
    fileupload_url = reverse_lazy('dashboard:fileupload')

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        elif self.action in ['retrieve', 'update', 'partial_update', 'delete']:
            instance = self.get_object()
            return self.detail_serializer_classes.get(instance._meta.label_lower,
                                                      self.detail_serializer_class)
        elif self.action == 'create':
            try:
                ctype = ContentType.objects.get_for_id(self.request.data.get('polymorphic_ctype'))
            except ContentType.DoesNotExist:
                # fallback to default detail serializer class
                return self.detail_serializer_class
            else:
                return self.detail_serializer_classes.get(ctype.model_class()._meta.label_lower,
                                                          self.detail_serializer_class)
        msg = "ViewSet 'ProductsDashboard' is not implemented for action '{}'"
        raise NotImplementedError(msg.format(self.action))

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        kwargs.update(context=context, label='dashboard')
        serializer = serializer_class(*args, **kwargs)
        return serializer

    @cached_property
    def list_fields(self):
        serializer = self.list_serializer_class()
        field_names = getattr(self, 'list_display', list(serializer.get_fields()))
        detail_links = getattr(self, 'list_display_links', [field_names[0]])

        list_fields = []
        for name, field in serializer.get_fields().items():
            field_type = field.style.get('field_type', 'string')
            bits = ['field("{}", "{}")'.format(name, field_type)]
            if name in detail_links:
                bits.append('isDetailLink(true)')
            list_fields.append(mark_safe('.'.join(bits)))

        return list_fields

    @cached_property
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
        fields = []
        if self.detail_serializer_classes:
            # add select box to choose product type
            pt_field = 'field("polymorphic_ctype", "choice").label("{}").choices({}).defaultValue({})'
            fields.append(mark_safe(pt_field.format(_("Product Type"),
                                                    json.dumps(choices, cls=JSONEncoder),
                                                    choices[0]['value'])))
        fields.extend(self.get_detail_fields(template))
        return fields

    @cached_property
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
        serializer_classes = self.detail_serializer_classes or {'product': self.detail_serializer_class}
        detail_fields = OrderedDict()
        for serializer_id, serializer_class in enumerate(serializer_classes.values()):
            for name, field in serializer_class().get_fields().items():
                try:
                    field_type, extra_bits, template_context = self.get_field_context(field)
                except HiddenDashboardField:
                    continue
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
            if len(ng_field.serializers) < len(serializer_classes):
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
        if field.read_only or field.style.get('hidden'):
            raise HiddenDashboardField
        extra_bits = ['validation({})'.format(json.dumps({'required': field.required}))]
        context = {'field_tag': 'ma-field', 'include_label': 'true'}
        if field.label is not None:
            extra_bits.append('label("{}")'.format(field.label))
        if field.default is not empty:
            if isinstance(field.default, bool):
                default_value = str(field.default).lower()
            elif isinstance(field.default, (float, int, Decimal)):
                default_value = field.default
            else:
                default_value = '"{}"'.format(field.default)
            extra_bits.append('defaultValue({})'.format(default_value))

        if isinstance(field, fields.BooleanField):
            field_type = 'boolean'
        elif isinstance(field, fields.IntegerField):
            field_type = 'number'
        elif isinstance(field, (fields.FloatField, fields.DecimalField)):
            field_type = 'float'
        elif isinstance(field, fields.EmailField):
            field_type = 'email'
        elif isinstance(field, TextField):
            field_type = 'wysiwyg'
        elif isinstance(field, serializers.CharField):
            field_type = 'string'
        elif isinstance(field, (fields.ChoiceField, relations.PrimaryKeyRelatedField)):
            field_type = 'choice'
            choices = [{'value': value, 'label': label} for value, label in field.choices.items()]
            extra_bits.append('choices({})'.format(json.dumps(choices, cls=JSONEncoder)))
        elif isinstance(field, fields.ImageField):
            field_type = 'file'
        elif isinstance(field, serializers.ListSerializer):
            field_type = 'embedded_list'
            target_fields = []
            for key, child_field in field.child.fields.items():
                try:
                    ch_ft, ch_xbits, ch_ctx = self.get_field_context(child_field)
                except HiddenDashboardField:
                    continue
                bits = ['nga.field("{}", "{}")'.format(key, ch_ft)] + ch_xbits
                target_fields.append('.'.join(bits))
            extra_bits.append('targetFields([' + ', '.join(target_fields) + '])')
        else:
            raise HiddenDashboardField

        # in case the field declares its own field type
        field_type = field.style.get('field_type', field_type)

        if field_type == 'file':
            extra_bits.append('uploadInformation({{"url": "{}"}})'.format(self.fileupload_url))

        return field_type, extra_bits, context

    def has_add_permission(self):
        """
        Returns True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        codename = get_permission_codename('add', ProductModel._meta)
        return self.request.user.has_perm('{}.{}'.format(app_settings.APP_LABEL, codename))
