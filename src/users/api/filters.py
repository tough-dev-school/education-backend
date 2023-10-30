from django_filters import rest_framework as filters

from products.models import Course
from users.models import User


class UserFilter(filters.FilterSet):
    course = filters.NumberFilter(method="filter_course")

    class Meta:
        model = User
        fields = ("course",)

    def filter_course(self, queryset, name, value):
        course = Course.objects.filter(pk=value).first()

        if course:
            return course.get_purchased_users().order_by("first_name", "last_name")
