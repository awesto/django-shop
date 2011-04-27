# -*- coding: utf-8 -*-
""" PolymorphicManager
    Please see README.rst or DOCS.rst or http://bserve.webhop.org/wiki/django_polymorphic
"""

from django.db import models
from query import PolymorphicQuerySet

class PolymorphicManager(models.Manager):
    """
    Manager for PolymorphicModel

    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    """
    use_for_related_fields = True

    def __init__(self, queryset_class=None, *args, **kwrags):
        if not queryset_class: self.queryset_class = PolymorphicQuerySet
        else: self.queryset_class = queryset_class
        super(PolymorphicManager, self).__init__(*args, **kwrags)

    def get_query_set(self):
        return self.queryset_class(self.model)

    # Proxy all unknown method calls to the queryset, so that its members are
    # directly accessible as PolymorphicModel.objects.*
    # The advantage of this method is that not yet known member functions of derived querysets will be proxied as well.
    # We exclude any special functions (__) from this automatic proxying.
    def __getattr__(self, name):
        if name.startswith('__'): return super(PolymorphicManager, self).__getattr__(self, name)
        return getattr(self.get_query_set(), name)

    def __unicode__(self):
        return self.__class__.__name__ + ' (PolymorphicManager) using ' + self.queryset_class.__name__

