from typing import no_type_check

from django import forms

from diplomas.models import Diploma
from products.models import Course
from studying.models import Study
from users.models import User


class DiplomaAddForm(forms.ModelForm):
    course = forms.ModelChoiceField(label="Курс", queryset=Course.objects.order_by("name"))
    student = forms.ModelChoiceField(label="Студент", queryset=User.objects.order_by("first_name", "last_name"))

    class Meta:
        model = Diploma
        fields = (
            "course",
            "student",
            "language",
        )

    class Media:
        js = ("admin/js/get_course_students.js",)

    @no_type_check
    def clean(self):
        data = super().clean()

        course, student = data.pop("course"), data.pop("student")

        study = Study.objects.filter(course=course, student=student).first()

        if not study:
            raise forms.ValidationError(f"Студент {student.get_full_name()} не обучался на курсе «{course.name}»!")

        if Diploma.objects.filter(study=study, language=data["language"]).exists():
            raise forms.ValidationError(f"Диплом для студента {student.get_full_name()} курса «{course.name}» на языке `{data['language']}` уже существует!")

        data["study"] = study

        return data
