from django_filters import rest_framework as filters

from apps.users.models import User


class UserFilterSet(filters.FilterSet):
    email = filters.CharFilter(field_name="email", lookup_expr="iexact")

    class Meta:
        model = User
        fields = ["email"]
