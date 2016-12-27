# -*- coding: utf-8 -*-
import copy
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.db import models
from django.utils import six
from django.utils.functional import SimpleLazyObject, empty
from shop import app_settings


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

    def __init__(self, to, **kwargs):
        super(ManyToManyField, self).__init__(to, **kwargs)

        through = kwargs.get('through')

        if through is None:
            self.abstract_through_model = None
        else:
            try:
                self.abstract_through_model = through._meta.object_name
            except AttributeError:
                assert isinstance(through, six.string_types), (
                    '%s(%r) is invalid. '
                    'Through parameter must be either a model or a model name'
                    % (self.__class__.__name__, through)
                )
                self.abstract_through_model = through
            else:
                assert through._meta.abstract, (
                    '%s can only define a through relation '
                    'with abstract class %s'
                    % (self.__class__.__name__, through._meta.object_name)
                )


class ForeignKeyBuilder(ModelBase):
    """
    Here the magic happens: All known and deferred foreign keys are mapped to their correct model's
    counterpart.
    If the main application stores its models in its own directory, add to settings.py:
    SHOP_APP_LABEL = 'myshop'
    so that the models are created inside your own shop instatiation.
    """
    _materialized_models = {}
    _pending_mappings = []

    def __new__(cls, name, bases, attrs):
        class Meta:
            app_label = app_settings.APP_LABEL

        attrs.setdefault('Meta', Meta)
        if not hasattr(attrs['Meta'], 'app_label') and not getattr(attrs['Meta'], 'abstract', False):
            attrs['Meta'].app_label = Meta.app_label
        attrs.setdefault('__module__', getattr(bases[-1], '__module__'))
        Model = super(ForeignKeyBuilder, cls).__new__(cls, name, bases, attrs)
        if Model._meta.abstract:
            return Model
        for baseclass in bases:
            # classes which materialize an abstract model are added to a mapping dictionary
            basename = baseclass.__name__
            try:
                if not issubclass(Model, baseclass) or not baseclass._meta.abstract:
                    raise ImproperlyConfigured("Base class %s is not abstract." % basename)
            except (AttributeError, NotImplementedError):
                pass
            else:
                if basename in cls._materialized_models:
                    if Model.__name__ != cls._materialized_models[basename]:
                        raise AssertionError("Both Model classes '%s' and '%s' inherited from abstract"
                            "base class %s, which is disallowed in this configuration." %
                            (Model.__name__, cls._materialized_models[basename], basename))
                elif isinstance(baseclass, cls):
                    cls._materialized_models[basename] = Model.__name__
                    # remember the materialized model mapping in the base class for further usage
                    baseclass._materialized_model = Model
                    cls.process_pending_mappings(Model, basename)

        cls.handle_deferred_foreign_fields(Model)
        Model.perform_model_checks()
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
                mapmodel = cls._materialized_models.get(member.abstract_model)

            abstract_through_model = getattr(member, 'abstract_through_model', None)
            mapmodel_through = cls._materialized_models.get(abstract_through_model)

            if mapmodel and (not abstract_through_model or mapmodel_through):
                if mapmodel_through:
                    member.options['through'] = mapmodel_through
                field = member.MaterializedField(mapmodel, **member.options)
                field.contribute_to_class(Model, attrname)
            else:
                ForeignKeyBuilder._pending_mappings.append((Model, attrname, member,))

    @staticmethod
    def process_pending_mappings(Model, basename):
        assert basename in ForeignKeyBuilder._materialized_models
        assert Model._materialized_model

        """
        Check for pending mappings and in case, process, and remove them from the list
        """
        for mapping in ForeignKeyBuilder._pending_mappings[:]:
            member = mapping[2]
            mapmodel = ForeignKeyBuilder._materialized_models.get(member.abstract_model)
            abstract_through_model = getattr(member, 'abstract_through_model', None)
            mapmodel_through = ForeignKeyBuilder._materialized_models.get(abstract_through_model)

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
    def perform_model_checks(cls):
        """
        Hook for each class inheriting from ForeignKeyBuilder, to perform checks on the
        implementation of the just created class type.
        """

    @classmethod
    def check_for_pending_mappings(cls):
        if cls._pending_mappings:
            msg = "Deferred foreign key '{0}.{1}' has not been mapped"
            pm = cls._pending_mappings
            raise ImproperlyConfigured(msg.format(pm[0][0].__name__, pm[0][1]))


class MaterializedModel(SimpleLazyObject):
    """
    Wrap the base model into a lazy object, so that we can refer to members of its
    materialized model using lazy evaluation.
    """
    def __init__(self, base_model):
        self.__dict__['_base_model'] = base_model
        super(SimpleLazyObject, self).__init__()

    def _setup(self):
        self._wrapped = getattr(self._base_model, '_materialized_model')

    def __call__(self, *args, **kwargs):
        # calls the constructor of the materialized model
        if self._wrapped is empty:
            self._setup()
        return self._wrapped(*args, **kwargs)

    def __deepcopy__(self, memo):
        if self._wrapped is empty:
            # We have to use SimpleLazyObject, not self.__class__, because the latter is proxied.
            result = MaterializedModel(self._base_model)
            memo[id(self)] = result
            return result
        else:
            return copy.deepcopy(self._wrapped, memo)

    def __repr__(self):
        if self._wrapped is empty:
            repr_attr = self._base_model
        else:
            repr_attr = self._wrapped
        return '<MaterializedModel: {}>'.format(repr_attr)

    def __instancecheck__(self, instance):
        if self._wrapped is empty:
            self._setup()
        return isinstance(instance, self._materialized_model)
