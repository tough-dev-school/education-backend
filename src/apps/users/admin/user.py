from typing import TYPE_CHECKING

from django.contrib.auth.admin import UserAdmin as StockUserAdmin

from apps.products.models import Course
from apps.users.models import User
from core.admin import admin

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(User)
class UserAdmin(StockUserAdmin):
    def get_search_results(self, request: "HttpRequest", queryset: "QuerySet", search_term: str) -> tuple["QuerySet", bool]:
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        course = request.GET.get("course")

        if course:
            course = Course.objects.filter(id=course).first()

            if course:
                queryset = course.get_purchased_users()

        return queryset, use_distinct
