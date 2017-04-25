# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict, namedtuple

from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template import Context, Template
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, Route, DynamicDetailRoute
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from shop import app_settings
from shop.models.product import ProductModel
from shop.money.serializers import JSONEncoder
from shop.rest.money import JSONRenderer
from shop.rest.renderers import DashboardRenderer
from shop.serializers.bases import ProductSerializer


class DashboardRouter(DefaultRouter):
    root_view_name = 'root'

    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Detail routes
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'delete': 'destroy',
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        Route(
            url=r'^{prefix}/add{trailing_slash}$',
            mapping={
                'get': 'new',
                'post': 'create',
            },
            name='{basename}-add',
            initkwargs={'suffix': 'New'}
        ),

        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_api_root_view(self, api_urls=None):
        dashboard_entities = OrderedDict()
        for prefix, viewset, basename in self.registry:
            dashboard_entities[prefix] = viewset()

        class RootView(APIView):
            """
            View to handle to root dashboard page.
            """
            renderer_classes = (TemplateHTMLRenderer,)
            template_name = 'shop/dashboard/main.html'

            def get(self, request, *args, **kwargs):
                context = {
                    'dashboard_entities': dashboard_entities,
                }
                return Response(context, template_name=self.template_name)

        return RootView.as_view()

router = DashboardRouter(trailing_slash=False)


class DashboardPaginator(LimitOffsetPagination):
    default_limit = 20


NgField = namedtuple('NgField', ['field_type', 'serializers'])


class ProductsDashboard(ModelViewSet):
    renderer_classes = (DashboardRenderer, JSONRenderer, BrowsableAPIRenderer)
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
        elif self.suffix == 'New':
            model = self.request.GET.get('model')
            return self.detail_serializer_classes.get(model, ProductSerializer)
        return self.list_serializer_class  # TODO: use the correct
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
            console.log(entry);
            {% spaceless %}{% with tag="ma-string-column" %}
            {% for ctype in ctypes %}
            return '<ma-field ng-if="entry.values.polymorphic_ctype=={{ ctype.id }}" field="::field" value="entry.values[field.name()]" entry="entry" entity="::entity"></ma-field>';
            {% endfor %}
            {% endwith %}{% endspaceless %}
        }, true)""")
        choices = []
        pt_field = 'field("polymorphic_ctype", "choice").label("{}").choices({})'
        for serializer_class in self.detail_serializer_classes.values():
            choices.append({
                'value': ContentType.objects.get_for_model(serializer_class.Meta.model).id,
                'label': serializer_class.Meta.model._meta.verbose_name,
            })
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
                return '<ma-field field="::field" value="entry.values[field.name()]" entry="entry" entity="::entity"></ma-field>';
            {% endfor %}
            {% endwith %}{% endspaceless %}
        }, true)""")
        # <ma-field field="::field" value="entry.values[field.name()]" entry="entry" entity="::entity" form="formController.form" datastore="::formController.dataStore" class="ng-scope ng-isolate-scope"><div id="row-images" class="form-field form-group has-feedback ng-scope" ng-class="getFieldValidationClass()">
        #template = '<span><ma-number-column field="::field" value="::entry.values[field.name()]"></ma-number-column></span>'
        return self.get_detail_fields(template)

    def get_detail_fields(self, template):
        detail_fields = OrderedDict()
        for serializer_id, serializer_class in enumerate(self.detail_serializer_classes.values()):
            for name, field in serializer_class().get_fields().items():
                field_type = field.style.get('field_type', 'string')
                if name in detail_fields:
                    if detail_fields[name].field_type != field_type:
                        detail_fields[name + str(serializer_id)] = NgField(field_type, [serializer_class])
                    else:
                        detail_fields[name].serializers.append(serializer_class)
                else:
                    detail_fields[name] = NgField(field_type, [serializer_class])

        #print(detail_fields)

        result_list = []
        for key, ng_field in detail_fields.items():
            bits = ['field("{}", "{}")'.format(key, ng_field.field_type)]
            if len(ng_field.serializers) < len(self.detail_serializer_classes):
                # this field it not available for all serializer classes,
                # handle polymorphism using a template to hide it conditionally
                ctypes = [ContentType.objects.get_for_model(sc.Meta.model) for sc in ng_field.serializers]
                context = Context({'ctypes': ctypes, 'field_type': ng_field.field_type})
                bits.append(template.render(context))
            result_list.append(mark_safe('.'.join(bits)))

        print(result_list)
        return result_list

    def Xget_list_display_links(self):
        if hasattr(self, 'list_display_links'):
            return self.list_display_links
        return self.get_list_display()[:1]

    def Xget_renderer_context(self):
        template_context = {
            'has_add_permission': self.has_add_permission(),
            #'has_change_permission': self.has_change_permission(obj),
            #'has_delete_permission': self.has_delete_permission(obj),
        }
        if self.suffix == 'List':
            list_display_fields = OrderedDict()
            serializer_class = self.list_serializer_class()
            for field_name in self.get_list_display():
                list_display_fields[field_name] = serializer_class.fields[field_name]
            template_context['list_display_fields'] = list_display_fields
            template_context['list_display_links'] = self.get_list_display_links()
            detail_models = []
            for name, serializer_class in self.detail_serializer_classes.items():
                detail_models.append((name, serializer_class.Meta.model._meta.verbose_name))
            template_context['detail_models'] = detail_models
            detail_url = reverse('dashboard:product-change', args=(':PK:',))
            template_context['detail_ng_href'] = detail_url.replace(':PK:', '{{ entry.pk }}')

        renderer_context = super(ProductsDashboard, self).get_renderer_context()
        renderer_context['template_context'] = template_context
        return renderer_context

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

    def new(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response({'serializer': serializer})

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
