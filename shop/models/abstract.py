# -*- coding: utf-8 -*-
import six
from django.db import models
from shop.deferred import ForeignKeyBuilder, DeferredForeignKey, DeferredManyToManyField


class AbstractModel1(six.with_metaclass(ForeignKeyBuilder, models.Model)):
    class Meta:
        abstract = True

    name = models.CharField(max_length=20)
    parent = DeferredForeignKey('AbstractModel1', blank=True, null=True, related_name='rel_parent')
    that = DeferredForeignKey('AbstractModel2', blank=True, null=True, related_name='rel_that')

    def __init__(self, *args, **kwargs):
        print "AbstractModel1.__init__"
        super(AbstractModel1, self).__init__(*args, **kwargs)


class AbstractModel2(six.with_metaclass(ForeignKeyBuilder, models.Model)):
    class Meta:
        abstract = True

    identifier = models.CharField(max_length=20)
    other = DeferredForeignKey(AbstractModel1, blank=True, null=True)
    ref = DeferredManyToManyField('AbstractModel3', blank=True, null=True)


class AbstractModel3(six.with_metaclass(ForeignKeyBuilder, models.Model)):
    class Meta:
        abstract = True

    identifier = models.CharField(max_length=20)
