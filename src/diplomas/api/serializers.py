from rest_framework import serializers

from diplomas.models import Diploma
from products.api.serializers import CourseSimpleSerializer
from users.api.serializers import UserSafeSerializer


class DiplomaSerializer(serializers.ModelSerializer):
    student = UserSafeSerializer(source='study.student')
    course = CourseSimpleSerializer(source='study.course')

    class Meta:
        model = Diploma
        fields = [
            'course',
            'slug',
            'language',
            'image',
            'student',
        ]
