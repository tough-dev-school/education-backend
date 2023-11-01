import contextlib
from copy import copy
from functools import reduce
import operator
from typing import Any, Type

from behaviors.behaviors import Timestamped

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property

__all__ = [
    "models",
    "DefaultModel",
    "TimestampedModel",
]


class DefaultModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        name = getattr(self, "name", None)
        if name is not None:
            return str(name)

        return super().__str__()

    @classmethod
    def get_contenttype(cls) -> ContentType:
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def has_field(cls, field: str) -> bool:
        """
        Shortcut to check if model has particular field
        """
        try:
            cls._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False

    def update_from_kwargs(self, **kwargs: dict[str, Any]) -> None:
        """
        A shortcut method to update model instance from the kwargs.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def setattr_and_save(self, key: str, value: Any) -> None:
        """Shortcut for testing -- set attribute of the model and save"""
        setattr(self, key, value)
        self.save()

    def copy(self, **kwargs: Any) -> "DefaultModel":
        """Creates new object from current."""
        instance = copy(self)
        kwargs.update(
            {
                "id": None,
                "pk": None,
            }
        )
        instance.update_from_kwargs(**kwargs)
        return instance

    @classmethod
    def get_label(cls) -> str:
        """
        Get a unique within the app model label
        """
        return cls._meta.label_lower.split(".")[-1]

    @classmethod
    def get_foreignkey(cls, Model: Type[models.Model]) -> str | None:
        """Given an model, returns the ForeignKey to it"""
        for field in cls._meta.get_fields():
            if isinstance(field, models.fields.related.ForeignKey):
                if field.related_model == Model:
                    return field.name

    def clear_cached_properties(self) -> None:
        """Clears all used cached properties of instance."""

        for property_name in self._get_cached_property_names():
            with contextlib.suppress(KeyError):
                del self.__dict__[property_name]

    def _get_cached_property_names(self) -> list[str]:
        return [func_name for func_name in dir(self.__class__) if type(getattr(self.__class__, func_name)) is cached_property]


class TimestampedModel(DefaultModel, Timestamped):
    """
    Default app model that has `created` and `updated` attributes.

    Currently based on https://github.com/audiolion/django-behaviors
    """

    class Meta:
        abstract = True


def only_one_or_zero_is_set(*fields: str) -> models.Q:
    """Generate a query for CheckConstraint that allows to set only one (or none of) given fields"""
    constraints = []
    for field in fields:
        constraint = models.Q(
            **{
                f"{field}__isnull": False,
                **{f"{empty_field}__isnull": True for empty_field in fields if empty_field != field},
            },
        )
        constraints.append(constraint)

    all_fields_can_empty_constraint = models.Q(
        **{f"{field}__isnull": True for field in fields},
    )

    constraints.append(all_fields_can_empty_constraint)

    return models.Q(reduce(operator.or_, constraints))
