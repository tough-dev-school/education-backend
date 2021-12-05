from typing import Optional

import contextlib
from behaviors.behaviors import Timestamped  # type: ignore
from copy import copy
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property

__all__ = [
    'models',
    'DefaultModel',
    'TimestampedModel',
]


class DefaultModel(models.Model):
    class Meta:
        abstract = True

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

        return None

    def clear_cached_properties(self) -> None:
        """Clears all used cached properties of instance."""

        for property_name in self._get_cached_property_names():
            with contextlib.suppress(KeyError):
                del self.__dict__[property_name]

    def _get_cached_property_names(self):
        return [
            func_name
            for func_name in dir(self.__class__)
            if type(getattr(self.__class__, func_name)) is cached_property
        ]

    def __str__(self) -> str:
        name = getattr(self, 'name', None)
        if name is not None:
            return str(name)

        return super().__str__()


class TimestampedModel(DefaultModel, Timestamped):
    """
    Default app model that has `created` and `updated` attributes.

    Currently based on https://github.com/audiolion/django-behaviors
    """
    class Meta:
        abstract = True


class EmailLogEntry(TimestampedModel):
    email = models.CharField(max_length=255, null=False)
    template_id = models.CharField(max_length=255, null=False)

    class Meta:
        index_together = ['email', 'template_id']
        unique_together = ['email', 'template_id']
