from typing import Any

from django.db.models import Model
from django.forms import ModelForm as _ModelForm


class ModelForm(_ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Adds ability to specify custom data as the initial value via get_custom_initial_data(instance)"""
        instance = kwargs.get("instance")
        initial = kwargs.get("initial") or dict()

        if instance is not None:
            initial.update(self.get_custom_initial_data(instance))

        kwargs.update(
            {
                "initial": initial,
                "instance": instance,
            }
        )

        super().__init__(*args, **kwargs)

    def get_custom_initial_data(self, instance: Model) -> dict[str, Any]:
        return {}


__all__ = [
    "ModelForm",
]
