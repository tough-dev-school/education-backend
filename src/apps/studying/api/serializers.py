from rest_framework import serializers

from apps.products.models import Course


class CourseSerializer(serializers.ModelSerializer):
    home_page_slug = serializers.CharField()

    class Meta:
        model = Course
        fields = [
            "id",
            "slug",
            "name",
            "home_page_slug",
            "cover",
        ]
