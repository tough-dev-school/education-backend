import datetime

from celery import group
from rest_framework.request import Request

from django import forms
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin
from diplomas.models import Diploma
from diplomas.models import DiplomaTemplate
from orders import tasks
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

    def clean(self) -> dict:
        data = super().clean()

        course = data.pop("course")  # type: ignore[union-attr]
        student = data.pop("student")  # type: ignore[union-attr]

        study = Study.objects.filter(course=course, student=student).first()

        if not study:
            raise forms.ValidationError(f"Студент {student.get_full_name()} не обучался на курсе «{course.name}»!")

        data["study"] = study  # type: ignore[index]

        if Diploma.objects.filter(study=study, language=data["language"]).exists():  # type: ignore[index]
            raise forms.ValidationError(f"Диплом для студента {student.get_full_name()} курса «{course.name}» на языке `{data['language']}` уже существует!")  # type: ignore[index]

        return data  # type: ignore[return-value]


@admin.register(Diploma)
class DiplomaAdmin(ModelAdmin):
    add_form = DiplomaAddForm
    form = DiplomaAddForm

    actions = ("send_to_student", "regenerate")
    fields = ("course", "student", "language", "image")
    list_display = (
        "date",
        "student",
        "course",
        "language",
        "homework_accepted",
    )
    list_filter = ("language", "study__course")
    list_select_related = ("study", "study__student", "study__course")
    raw_id_fields = ("study",)
    readonly_fields = ("slug",)
    search_fields = (
        "study__student__first_name",
        "study__student__last_name",
        "study__student__email",
    )

    def save_model(self, request: "HttpRequest", obj: "Diploma", form: "DiplomaAddForm", change: bool) -> None:
        obj = form.save(commit=False)

        obj.study = form.cleaned_data["study"]
        obj.save()

    @admin.display(description=_("Course"), ordering="study__course")
    def course(self, diploma: Diploma) -> Course:
        return diploma.study.course

    @admin.display(description=_("Date"), ordering="created")
    def date(self, diploma: Diploma) -> datetime.datetime:
        return diploma.modified or diploma.created

    @admin.display(description=_("Homework"), ordering="study__homework_accepted", boolean=True)
    def homework_accepted(self, diploma: Diploma) -> bool:
        return diploma.study.homework_accepted

    @admin.display(description=_("Student"), ordering="study__student")
    def student(self, diploma: Diploma) -> User:
        return diploma.study.student

    @admin.action(description=_("Send diploma to student"))
    def send_to_student(self, request: Request, queryset: QuerySet) -> None:
        for diploma in queryset.iterator():
            diploma.send_to_student()

        self.message_user(request, f"Diplomas sent to {queryset.count()} students")

    @admin.action(description=_("Regenerate diploma"))
    def regenerate(self, request: Request, queryset: QuerySet) -> None:
        order_ids = queryset.values_list("study__order_id", flat=True).distinct()

        generate_diplomas = group([tasks.generate_diploma.s(order_id=order_id) for order_id in order_ids])
        generate_diplomas.skew(step=2).apply_async()

        self.message_user(request, f"Started generation of {len(order_ids)} diplomas")


@admin.register(DiplomaTemplate)
class DiplomaTemplateAdmin(ModelAdmin):
    fields = list_display = (
        "course",
        "language",
        "slug",
        "homework_accepted",
    )

    list_editable = [
        "slug",
        "language",
        "homework_accepted",
    ]
