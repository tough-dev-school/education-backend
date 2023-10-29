import datetime

from celery import group
from rest_framework.request import Request

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin
from diplomas.admin.forms import DiplomaForm
from diplomas.models import Diploma
from orders import tasks
from products.models import Course
from users.models import User


@admin.register(Diploma)
class DiplomaAdmin(ModelAdmin):
    form = DiplomaForm

    actions = ("send_to_student", "regenerate")
    fields = (
        "slug",
        "course",
        "student",
        "language",
        "image",
    )
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

    def save_model(self, request: "HttpRequest", obj: "Diploma", form: "DiplomaForm", change: bool) -> None:
        if not change:
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
