from apps.lms.models import Module
from core.admin import ModelAdmin, admin


@admin.register(Module)
class ModuleAdmin(ModelAdmin): ...


__all__ = [
    "Module",
]
