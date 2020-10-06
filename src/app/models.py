import inspect
from copy import copy
from typing import Generator, Optional

from behaviors.behaviors import Timestamped
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property

__all__ = [
    'models',
    'DefaultManager',
    'DefaultModel',
    'DefaultQuerySet',
    'TimestampedModel',
]


class DefaultQuerySet(models.QuerySet):
    Q = None
    """Q is a extension to Django queryset. Defining Q like this:
        class Q:
            @staticmethod
            def delivered():
                return Q(status__extended='delivered')

        Adds the method `delivered` to the queryset (and manager built on it), and
        allows you to reuse the returned Q object, like this:

        class OrderQuerySet:
            class Q:
                @staticmethod
                def delivered():
                    return Q(status__extended='delivered')

            def delivered_yesterday(self):
                return self.filter(self.Q.delivered & Q(delivery_date='2032-12-01'))
    """

    @classmethod
    def as_manager(cls):
        """Copy-paste of stock django as_manager() to use our default manager

        See also: https://github.com/django/django/blob/master/django/db/models/query.py#L198
        """
        manager = DefaultManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True

    def __getattr__(self, name):
        if self.Q is not None and hasattr(self.Q, name):
            return lambda *args: self.filter(getattr(self.Q, name)())

        raise AttributeError()

    def with_last_update(self):
        """Annotate `last_update` field that displays the creation or modification date"""
        return self.annotate(last_update=Coalesce(F('modified'), F('created')))


class DefaultManager(models.Manager):
    relations_to_assign_after_creation = []

    def __getattr__(self, name):
        if hasattr(self._queryset_class, 'Q') and hasattr(self._queryset_class.Q, name):
            return getattr(self.get_queryset(), name)

        raise AttributeError(f'Nor {self.__class__}, nor {self._queryset_class.__name__} or {self._queryset_class.__name__}.Q does not have `{name}` defined.')


class DefaultModel(models.Model):
    objects = DefaultManager()

    class Meta:
        abstract = True

    @classmethod
    def _should_track_fields(cls) -> bool:
        return getattr(cls, '_enable_field_tracking', False)

    def _save_original_field_values(self):
        self._original_field_values = {field: self._getattr_for_field_tracking(field) for field in self._tracking_handlers_for_fields}

    def _getattr_for_field_tracking(self, attr):
        """Avoid N+1 for foreignkeys, store there id instead of value"""
        if isinstance(getattr(self.__class__, attr), GenericForeignKey):  # return the instance for ContentType attributes. Caution, this does N+1
            return getattr(self, attr, None)

        # Try to return ID instead of instance
        return getattr(self, f'{attr}_id', None) or getattr(self, attr, None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self._should_track_fields():  # populate instance with original values
            self._save_original_field_values()

    def refresh_from_db(self):
        super().refresh_from_db()

        if self._should_track_fields():
            self._save_original_field_values()

    def save(self, *args, disable_field_tracking=False, **kwargs):
        if disable_field_tracking or not self._should_track_fields() or not hasattr(self, '_original_field_values'):  # field tracking is disabled or was not initialized
            return super().save(*args, **kwargs)

        original_field_values = self._original_field_values.copy()
        super().save(*args, **kwargs)

        for field_name, handler in self._tracking_handlers_for_fields.items():

            current_value = self._getattr_for_field_tracking(field_name)
            original_value = original_field_values[field_name]

            if current_value == original_value:
                continue

            handler.send(
                instance=self,
                field_name=field_name,
                original_value=original_value,
                current_value=current_value,
                sender=self,
            )

        self._save_original_field_values()  # re-populate original field values after creation

    @classmethod
    def get_contenttype(cls) -> ContentType:
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def has_field(cls, field) -> bool:
        """
        Shortcut to check if model has particular field
        """
        try:
            cls._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False

    @classmethod
    def list_fields(cls, include_parents=True) -> Generator:
        """
        Shortcut to list all field names.

        Accepts parameter `include_parents=False` with which returnes only fields defined in current model.
        This behaviour is little different from django's — its _meta.get_fields(include_parents=False) returns
        fields taken from inherited models, and we do not
        """
        if include_parents:
            return (field.name for field in cls._meta.get_fields(include_parents=True) if not isinstance(field, GenericRelation))

        else:
            parent_fields = set()

            for parent in inspect.getmro(cls):
                if issubclass(parent, models.Model) and hasattr(parent, '_meta'):  # if it is a django model
                    if not issubclass(parent, cls):  # ignore the lowest model in tree
                        for field in parent._meta.get_fields(include_parents=False):
                            if not isinstance(field, GenericRelation):
                                parent_fields.update([field.name])

            return (field.name for field in cls._meta.get_fields(include_parents=False) if field.name not in parent_fields)

    def update_from_kwargs(self, **kwargs):
        """
        A shortcut method to update model instance from the kwargs.
        """
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def setattr_and_save(self, key, value):
        """Shortcut for testing -- set attribute of the model and save"""
        setattr(self, key, value)
        self.save()

    def copy(self, **kwargs):
        """Creates new object from current."""
        instance = copy(self)
        kwargs.update({
            'id': None,
            'pk': None,
        })
        instance.update_from_kwargs(**kwargs)
        return instance

    @classmethod
    def get_label(cls) -> str:
        """
        Get a unique within the app model label
        """
        return cls._meta.label_lower.split('.')[-1]

    @classmethod
    def get_foreignkey(cls, Model) -> Optional[str]:
        """Given an model, returns the ForeignKey to it"""
        for field in cls._meta.get_fields():
            if isinstance(field, models.fields.related.ForeignKey):
                if field.related_model == Model:
                    return field.name

    def clear_cached_properties(self):
        """Clears all used cached properties of instance."""

        for property_name in self._get_cached_property_names():
            try:
                del self.__dict__[property_name]
            except KeyError:
                pass

    def _get_cached_property_names(self):
        return [
            func_name
            for func_name in dir(self.__class__)
            if type(getattr(self.__class__, func_name)) is cached_property
        ]

    def __str__(self):
        if hasattr(self, 'name'):
            return str(self.name)

        return super().__str__()


class TimestampedModel(DefaultModel, Timestamped):
    """
    Default app model that has `created` and `updated` attributes.

    Currently based on https://github.com/audiolion/django-behaviors
    """
    class Meta:
        abstract = True
