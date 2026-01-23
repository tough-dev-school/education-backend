from rest_framework import serializers

from apps.lms.models import CourseLink
from apps.products.models import Course


class CourseLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLink
        fields = ["name", "url"]


class CourseSerializer(serializers.ModelSerializer):
    home_page_slug = serializers.CharField()
    links = CourseLinkSerializer(many=True, read_only=True, source="courselink_set")
    tariff_name = serializers.CharField(required=True, allow_null=True)
    cover = serializers.ImageField(required=True, allow_null=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "slug",
            "name",
            "product_name",
            "tariff_name",
            "home_page_slug",
            "cover",
            "chat",
            "calendar_ios",
            "calendar_google",
            "links",
        ]
