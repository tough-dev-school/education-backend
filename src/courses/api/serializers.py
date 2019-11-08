from rest_framework import serializers

from courses.models import Course, Record


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'slug',
            'name',
        ]


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = [
            'slug',
            'name',
        ]
