from rest_framework import serializers

from products.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'slug',
            'name',
        ]
