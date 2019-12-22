from rest_framework import serializers

from courses.models import Bundle, Course, Record


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


class BundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bundle
        fields = [
            'slug',
            'name',
        ]


class PurchaseSerializer(serializers.Serializer):
    """Simple serializer used to validate purchases"""

    class Meta:
        fields = [
            'name',
            'email',
        ]

    @classmethod
    def _validate(cls, input: dict):
        instance = cls(data=input)
        instance.is_valid(raise_exception=True)
