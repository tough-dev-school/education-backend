from rest_framework import serializers

from apps.products.models import Course


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug")
    home_page_slug = serializers.CharField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "home_page_slug",
            "cover",
        ]
