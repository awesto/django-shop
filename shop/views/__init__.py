# -*- coding: utf-8 -*-
from django import VERSION as django_version

if django_version[0] >= 1 and django_version[1] >= 3:  # pragma: no cover
    from django.views.generic import (TemplateView, ListView, DetailView, View)
    from django.views.generic.base import TemplateResponseMixin
else:  # pragma: no cover
    from cbv import (TemplateView, ListView, DetailView, View)  # NOQA
    from cbv.views.base import TemplateResponseMixin  # NOQA


class ShopTemplateView(TemplateView):
    """
    A class-based view for use within the shop (this allows to keep the above
    import magic in only one place)

    As defined by
    http://docs.djangoproject.com/en/dev/topics/class-based-views/

    Stuff defined here (A.K.A this is a documentation proxy for the above
    link):
    ---------------------------------------------------------------------
    self.template_name : Name of the template to use for rendering
    self.get_context_data(): Returns the context {} to render the template with
    self.get(request, *args, **kwargs): called for GET methods
    """


class ShopListView(ListView):
    """
    This is just to abstract the "Django version switching magic happening up
    there
    """


class ShopDetailView(DetailView):
    """
    This is just to abstract the "Django version switching magic happening up
    there
    """


class ShopView(View):
    """
    An abstraction of the basic view
    """


class ShopTemplateResponseMixin(TemplateResponseMixin):
    """
    An abstraction to solve the import problem for the template response mixin
    """
