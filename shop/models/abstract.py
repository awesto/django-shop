# -*- coding: utf-8 -*-
from six import with_metaclass
from django.db import models
from django.utils import six
from shop.models import deferred


class AbstractModel1(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    class Meta:
        abstract = True

    name = models.CharField(max_length=20)
    parent = deferred.ForeignKey('AbstractModel1', blank=True, null=True, related_name='rel_parent')
    that = deferred.ForeignKey('AbstractModel2', blank=True, null=True, related_name='rel_that')


class AbstractModel2(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    class Meta:
        abstract = True

    identifier = models.CharField(max_length=20)
    other = deferred.ForeignKey(AbstractModel1, blank=True, null=True)
    ref = deferred.ManyToManyField('AbstractModel3', blank=True, null=True)


class AbstractModel3(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    class Meta:
        abstract = True

    identifier = models.CharField(max_length=20)
    oneone = deferred.OneToOneField(AbstractModel2, blank=True, null=True)
