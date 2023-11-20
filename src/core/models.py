import operator
from functools import reduce
from typing import Any

from behaviors.behaviors import Timestamped
from django.db import models

__all__ = [
    "models",
    "DefaultModel",
    "TimestampedModel",
]


class TestUtilsMixin:
    def update(self: "models.Model", **kwargs: "Any") -> "models.Model":  # type: ignore[misc]
        for key, value in kwargs.items():
            setattr(self, key, value)

        update_fields = list(kwargs) + ["modified"] if hasattr(self, "modified") else list(kwargs)

        self.save(update_fields=update_fields)

        return self


class DefaultModel(TestUtilsMixin, models.Model):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        name = getattr(self, "name", None)
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
