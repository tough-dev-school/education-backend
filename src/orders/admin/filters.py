from django.utils.translation import gettext_lazy as _

from app.admin.filters import DefaultBooleanFilter


class IsActivePromocodeFilter(DefaultBooleanFilter):
    title = _('Active')
    parameter_name = 'active'
    default_value = True
