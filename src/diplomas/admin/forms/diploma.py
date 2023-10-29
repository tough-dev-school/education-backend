from typing import no_type_check

from django import forms

from diplomas.models import Diploma
from products.models import Course
from studying.models import Study
from users.models import User


class DiplomaForm(forms.ModelForm):
    course = forms.ModelChoiceField(label="Курс", queryset=Course.objects.order_by("name"))
    student = forms.ModelChoiceField(label="Студент", queryset=User.objects.order_by("first_name", "last_name"))

    class Meta:
        model = Diploma
        fields = (
            "course",
            "image",
            "language",
            "student",
        )
        labels = {
            "image": "Обложка",
            "language": "Язык",
            "slug": "Слаг",
        }

    class Media:
        js = ("admin/js/get_course_students.js",)

    @no_type_check
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.diploma = kwargs.get("instance")

        if self.diploma:
            self.fields["course"].disabled = True
            self.fields["course"].initial = self.diploma.study.course
            self.fields["course"].widget.attrs.update({"style": "background-color: rosybrown;"})

            self.fields["language"].initial = self.diploma.language

            self.fields["student"].disabled = True
            self.fields["student"].initial = self.diploma.study.student
            self.fields["student"].widget.attrs.update({"style": "background-color: rosybrown;"})

    @no_type_check
    def clean(self):  # noqa: CCR001
        data = super().clean()

        if not self.diploma:
            for fieldname in ("course", "image", "language", "student"):
                if not data.get(fieldname):
                    raise forms.ValidationError("")

            course, student = data.pop("course"), data.pop("student")

            study = Study.objects.filter(course=course, student=student).first()

            if not study:
                raise forms.ValidationError(f"Студент {student.get_full_name()} не обучался на курсе «{course.name}»!")

            data["study"] = study

            self.check_duplicate_diploma(data["language"], study)

        if self.diploma and data["language"] != self.diploma.language:
            self.check_duplicate_diploma(data["language"], self.diploma.study)

        return data

    def check_duplicate_diploma(self, language: str, study: "Study") -> None:
        if Diploma.objects.filter(language=language, study=study).exists():
            raise forms.ValidationError(f"Диплом для этого студента на языке `{language}` уже существует!")
