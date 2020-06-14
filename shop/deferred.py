# -*- coding: utf-8 -*-
import copy
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.db import models
from django.utils.functional import LazyObject, empty
from polymorphic.models import PolymorphicModelBase

from shop.conf import app_settings


class DeferredRelatedField:
    def __init__(self, to, **kwargs):
        try:
            self.abstract_model = to._meta.object_name
        except AttributeError:
            assert isinstance(to, str), "%s(%r) is invalid. First parameter must be either a model or a model name" % (self.__class__.__name__, to)
            self.abstract_model = to
        self.options = dict(**kwargs)


class OneToOneField(DeferredRelatedField):
    """
    Use this class to specify a one-to-one key in abstract classes. It will be converted into a real
    ``OneToOneField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.OneToOneField

    def __init__(self, to, on_delete, **kwargs):
        super().__init__(to, on_delete=on_delete, **kwargs)


class ForeignKey(DeferredRelatedField):
    """
    Use this class to specify foreign keys in abstract classes. It will be converted into a real
    ``ForeignKey`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ForeignKey

    def __init__(self, to, on_delete, **kwargs):
        super().__init__(to, on_delete=on_delete, **kwargs)


class ManyToManyField(DeferredRelatedField):
    """
    Use this class to specify many-to-many keys in abstract classes. They will be converted into a
    real ``ManyToManyField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ManyToManyField

    def __init__(self, to, **kwargs):
        super().__init__(to, **kwargs)

        through = kwargs.get('through')

        if through is None:
            self.abstract_through_model = None
        else:
            try:
                self.abstract_through_model = through._meta.object_name
            except AttributeError:
                assert isinstance(through, str), ('%s(%r) is invalid. '
                    'Through parameter must be either a model or a model name'
                    % (self.__class__.__name__, through))
                self.abstract_through_model = through


class ForeignKeyBuilder(ModelBase):
    """
    In Django we can not point a ``OneToOneField``, ``ForeignKey`` or ``ManyToManyField`` onto
    an abstract Model class. In Django-SHOP this limitation is circumvented by creating deferred
    foreign keys, which are mapped to their correct model's counterpart during the model
    materialization step.

    If the main application stores its models in its own directory, add to settings.py:
    SHOP_APP_LABEL = 'myshop', so that the models are created inside your own shop instantiation.
    """
    _model_allocation = {}
    _pending_mappings = []
    _materialized_models = {}

    def __new__(cls, name, bases, attrs):
        class Meta:
            app_label = app_settings.APP_LABEL

        attrs.setdefault('Meta', Meta)
        attrs.setdefault('__module__', getattr(bases[-1], '__module__'))
        if not hasattr(attrs['Meta'], 'app_label') and not getattr(attrs['Meta'], 'abstract', False):
            attrs['Meta'].app_label = Meta.app_label

        Model = super().__new__(cls, name, bases, attrs)

        if Model._meta.abstract:
            return Model

        if any(isinstance(base, cls) for base in bases):
            for baseclass in bases:
                if not isinstance(baseclass, cls):
                    continue

                assert issubclass(baseclass, models.Model)

                basename = baseclass.__name__

                if baseclass._meta.abstract:
                    if basename in cls._model_allocation:
                        raise ImproperlyConfigured(
                            "Both Model classes '%s' and '%s' inherited from abstract "
                            "base class %s, which is disallowed in this configuration."
                            % (Model.__name__, cls._model_allocation[basename], basename)
                        )

                    cls._model_allocation[basename] = Model.__name__
                    # remember the materialized model mapping in the base class for further usage
                    baseclass._materialized_model = Model
                    cls.process_pending_mappings(Model, basename)

        else:
            # Non abstract model that uses this Metaclass
            basename = Model.__name__
            cls._model_allocation[basename] = basename
            Model._materialized_model = Model
            cls.process_pending_mappings(Model, basename)

        cls.handle_deferred_foreign_fields(Model)
        cls.perform_meta_model_check(Model)
        cls._materialized_models[name] = Model
        return Model

    @classmethod
    def handle_deferred_foreign_fields(cls, Model):
        """
        Search for deferred foreign fields in our Model and contribute them to the class or
        append them to our list of pending mappings
        """
        for attrname in dir(Model):
            try:
                member = getattr(Model, attrname)
            except AttributeError:
                continue

            if not isinstance(member, DeferredRelatedField):
                continue

            if member.abstract_model == 'self':
                mapmodel = Model
            else:
                mapmodel = cls._model_allocation.get(member.abstract_model)

            abstract_through_model = getattr(member, 'abstract_through_model', None)
            mapmodel_through = cls._model_allocation.get(abstract_through_model)

            if mapmodel and (not abstract_through_model or mapmodel_through):
                if mapmodel_through:
                    member.options['through'] = mapmodel_through
                field = member.MaterializedField(mapmodel, **member.options)
                field.contribute_to_class(Model, attrname)
            else:
                ForeignKeyBuilder._pending_mappings.append((Model, attrname, member,))

    @staticmethod
    def process_pending_mappings(Model, basename):
        assert basename in ForeignKeyBuilder._model_allocation
        assert Model._materialized_model

        """
        Check for pending mappings and in case, process, and remove them from the list
        """
        for mapping in ForeignKeyBuilder._pending_mappings[:]:
            member = mapping[2]
            mapmodel = ForeignKeyBuilder._model_allocation.get(member.abstract_model)
            abstract_through_model = getattr(member, 'abstract_through_model', None)
            mapmodel_through = ForeignKeyBuilder._model_allocation.get(abstract_through_model)

            if member.abstract_model == basename or abstract_through_model == basename:
                if member.abstract_model == basename and abstract_through_model and not mapmodel_through:
                    continue
                elif abstract_through_model == basename and not mapmodel:
                    continue

                if mapmodel_through:
                    member.options['through'] = mapmodel_through

                field = member.MaterializedField(mapmodel, **member.options)
                field.contribute_to_class(mapping[0], mapping[1])
                ForeignKeyBuilder._pending_mappings.remove(mapping)

    def __getattr__(self, key):
        if key == '_materialized_model':
            msg = "No class implements abstract base model: `{}`."
            raise ImproperlyConfigured(msg.format(self.__name__))
        return object.__getattribute__(self, key)

    @classmethod
    def perform_meta_model_check(cls, Model):
        """
        Hook for each meta class inheriting from ForeignKeyBuilder, to perform checks on the
        implementation of the just created type.
        """

    @classmethod
    def check_for_pending_mappings(cls):
        if cls._pending_mappings:
            msg = "Deferred foreign key '{0}.{1}' has not been mapped"
            pm = cls._pending_mappings
            raise ImproperlyConfigured(msg.format(pm[0][0].__name__, pm[0][1]))


class PolymorphicForeignKeyBuilder(ForeignKeyBuilder, PolymorphicModelBase):
    """
    Base class for PolymorphicProductMetaclass
    """


class MaterializedModel(LazyObject):
    """
    Wrap the base model into a lazy object, so that we can refer to members of its
    materialized model using lazy evaluation.
    """
    def __init__(self, base_model):
        self.__dict__['_base_model'] = base_model
        super().__init__()

    def _setup(self):
        self._wrapped = getattr(self._base_model, '_materialized_model')

    def __call__(self, *args, **kwargs):
        # calls the constructor of the materialized model
        if self._wrapped is empty:
            self._setup()
        return self._wrapped(*args, **kwargs)

    def __copy__(self):
        if self._wrapped is empty:
            # If uninitialized, copy the wrapper. Use type(self),
            # not self.__class__, because the latter is proxied.
            return type(self)(self._base_model)
        else:
            # In Python 2.7 we can't return `copy.copy(self._wrapped)`,
            # it fails with `TypeError: can't pickle int objects`.
            # In Python 3 it works, because it checks if the copied value
            # is a subclass of `type`.
            # In this case it just returns the value.
            # As we know that self._wrapped is a subclass of `type`,
            # we can just return it here.
            return self._wrapped

    def __deepcopy__(self, memo):
        if self._wrapped is empty:
            # We have to use type(self), not self.__class__,
            # because the latter is proxied.
            result = type(self)(self._base_model)
            memo[id(self)] = result
            return result
        return copy.deepcopy(self._wrapped, memo)

    def __repr__(self):
        if self._wrapped is empty:
            repr_attr = self._base_model
        else:
            repr_attr = self._wrapped
        return '<MaterializedModel: {}>'.format(repr_attr)
