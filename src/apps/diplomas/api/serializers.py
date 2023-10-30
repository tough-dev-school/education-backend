from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.diplomas.models import Diploma
from apps.products.api.serializers import CourseSimpleSerializer
from apps.studying.models import Study
from apps.users.api.serializers import UserSafeSerializer


class DiplomaSerializer(serializers.ModelSerializer):
    student = UserSafeSerializer(source="study.student")
    course = CourseSimpleSerializer(source="study.course")
    url = serializers.URLField(source="get_absolute_url")

    class Meta:
        model = Diploma
        fields = [
            "course",
            "slug",
            "language",
            "image",
            "student",
            "url",
        ]


class DiplomaRetrieveSerializer(serializers.ModelSerializer):
    student = UserSafeSerializer(source="study.student")
    course = CourseSimpleSerializer(source="study.course")
    other_languages = serializers.SerializerMethodField()

    class Meta:
        model = Diploma
        fields = [
            "course",
            "slug",
            "language",
            "image",
            "student",
            "other_languages",
        ]

    def get_other_languages(self, diploma: Diploma) -> dict:
        return DiplomaSerializer(diploma.get_other_languages(), many=True).data


class DiplomaCreateSerializer(serializers.ModelSerializer):
    student = serializers.IntegerField(source="study.student_id")
    course = serializers.IntegerField(source="study.course_id")

    class Meta:
        model = Diploma
        fields = [
            "student",
            "course",
            "language",
            "image",
        ]

    def create(self, validated_data: dict) -> Diploma:
        validated_study_data = validated_data.pop("study")

        validated_data["study"] = self.get_study(
            student_id=validated_study_data["student_id"],
            course_id=validated_study_data["course_id"],
        )

        return super().create(validated_data)

    @staticmethod
    def get_study(student_id: str, course_id: str) -> Study | None:
        try:
            return Study.objects.get(student__id=student_id, course_id=course_id)
        except Study.DoesNotExist:
            raise ValidationError("Cant find student, course, or student purchased that course")
