# -*- coding: utf-8 -*-
from django.db.models.base import ModelBase
from django.db import models
from django.utils import six


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


class OneToOneField(DeferredRelatedField):
    """
    Use this class to specify a one-to-one key in abstract classes. It will be converted into a real
    ``OneToOneField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.OneToOneField


class ForeignKey(DeferredRelatedField):
    """
    Use this class to specify foreign keys in abstract classes. It will be converted into a real
    ``ForeignKey`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ForeignKey


class ManyToManyField(DeferredRelatedField):
    """
    Use this class to specify many-to-many keys in abstract classes. They will be converted into a
    real ``ManyToManyField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ManyToManyField


class ForeignKeyBuilder(ModelBase):
    _materialized_models = {}
    _pending_mappings = []

    def __new__(cls, name, bases, attrs):
        meta = attrs.setdefault('Meta', type('Meta', (), {}))
        if not hasattr(meta, 'app_label'):
            meta.app_label = cls.app_label
        model = super(ForeignKeyBuilder, cls).__new__(cls, name, bases, attrs)
        if model._meta.abstract:
            return model
        for baseclass in bases:
            # classes which materialize an abstract model are added to a mapping dictionary
            basename = baseclass.__name__
            try:
                if not issubclass(model, baseclass) or not baseclass._meta.abstract:
                    raise NotImplementedError()
            except (AttributeError, NotImplementedError):
                pass
            else:
                if basename in cls._materialized_models:
                    if model.__name__ != cls._materialized_models[basename]:
                        raise AssertionError("Both Model classes '%s' and '%s' inherited from abstract"
                            "base class %s, which is disallowed in this configuration." %
                            (model.__name__, cls._materialized_models[basename], basename))
                else:
                    cls._materialized_models[basename] = model.__name__
                    # remember the materialized model mapping in the base class for further usage
                    baseclass.materialized_model = model

            # check for pending mappings and in case, process them
            new_mappings = []
            for mapping in cls._pending_mappings:
                if mapping[2].abstract_model == baseclass.__name__:
                    field = mapping[2].MaterializedField(model, **mapping[2].options)
                    field.contribute_to_class(mapping[0], mapping[1])
                else:
                    new_mappings.append(mapping)
            cls._pending_mappings = new_mappings

        # search for deferred foreign fields in our model
        for attrname in dir(model):
            try:
                member = getattr(model, attrname)
            except AttributeError:
                continue
            if not isinstance(member, DeferredRelatedField):
                continue
            mapmodel = cls._materialized_models.get(member.abstract_model)
            if mapmodel:
                field = member.MaterializedField(mapmodel, **member.options)
                field.contribute_to_class(model, attrname)
            else:
                cls._pending_mappings.append((model, attrname, member,))
        return model
