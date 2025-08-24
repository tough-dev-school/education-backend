from apps.a12n.models import JWTBlacklist
from core.admin import ModelAdmin, admin


@admin.register(JWTBlacklist)
class JWTBlackListAdmin(ModelAdmin): ...
