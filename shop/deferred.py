# -*- coding: utf-8 -*-
import six
from django.db.models.base import ModelBase
from django.db import models


class DeferredRelatedField(object):
    def __init__(self, to, **kwargs):
        try:
            self.abstract_model = to._meta.object_name
        except AttributeError:
            assert isinstance(to, six.string_types), "%s(%r) is invalid. First parameter must be either a model or a model name" % (self.__class__.__name__, to)
            self.abstract_model = to
        else:
            assert to._meta.abstract, "%s can only define a relation with abstract class %s" % (self.__class__.__name__, to._meta.object_name)
        self.options = kwargs


class DeferredOneToOneField(DeferredRelatedField):
    """
    Use this class to specify a one-to-one key in abstract classes. It will be converted into a real
    ``OneToOneField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.OneToOneField


class DeferredForeignKey(DeferredRelatedField):
    """
    Use this class to specify foreign keys in abstract classes. It will be converted into a real
    ``ForeignKey`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ForeignKey


class DeferredManyToManyField(DeferredRelatedField):
    """
    Use this class to specify many-to-many keys in abstract classes. They will be converted into a
    real ``ManyToManyField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ManyToManyField


class ForeignKeyBuilder(ModelBase):
    _derived_models = {}
    _pending_mappings = []

    def __new__(cls, name, bases, attrs):
        model = super(ForeignKeyBuilder, cls).__new__(cls, name, bases, attrs)
        if model._meta.abstract:
            return model
        for baseclass in bases:
            if not issubclass(model, baseclass):
                continue
            if baseclass.__name__ in cls._derived_models:
                if model.__name__ != cls._derived_models[baseclass.__name__]:
                    raise AssertionError("Both Model classes '{0}' and '{1}' inherited" +
                        "from abstract base class {2}, which is disallowed in this configuration.")
            else:
                cls._derived_models[baseclass.__name__] = model.__name__
                # check for pending mappings and in case, process them
                new_mappings = []
                for mapping in cls._pending_mappings:
                    if mapping[2].abstract_model == baseclass.__name__:
                        field = mapping[2].MaterializedField(model.__name__, **mapping[2].options)
                        field.contribute_to_class(mapping[0], mapping[1])
                    else:
                        new_mappings.append(mapping)
                cls._pending_mappings = new_mappings

        # search for deferred foreign fields in our model
        for attrname in dir(model):
            member = getattr(model, attrname)
            if not isinstance(member, DeferredRelatedField):
                continue
            mapmodel = cls._derived_models.get(member.abstract_model)
            if mapmodel:
                field = member.MaterializedField(mapmodel, **member.options)
                field.contribute_to_class(model, attrname)
            else:
                cls._pending_mappings.append((model, attrname, member,))
        return model
