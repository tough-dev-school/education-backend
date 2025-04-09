from typing import Any

from django import forms
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from apps.homework import tasks
from apps.homework.models import Question
from apps.lms.models import Lesson, Module
from apps.products.models import Course
from core.admin import ModelAdmin, admin


class QuestionForm(forms.ModelForm):
    course = forms.ModelChoiceField(label=_("Course"), queryset=Course.objects.for_admin(), required=False)
    module = forms.ModelChoiceField(label=_("Module"), queryset=Module.objects.for_admin(), required=False)
    lesson = forms.ModelChoiceField(label=_("Lesson"), queryset=Lesson.objects.for_admin(), required=False)

    class Meta:
        model = Question
        fields = [
            "courses",
            "name",
            "deadline",
            "course",
            "module",
            "lesson",
            "text",
        ]

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/limit_module_choices.js",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Populate lesson, module and course during edit"""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lesson = Lesson.objects.filter(question=self.instance).select_related("module").first()
            if lesson:
                self.fields["lesson"].initial = lesson
                self.fields["module"].initial = lesson.module_id
                self.fields["course"].initial = lesson.module.course_id

    def save(self, commit: bool | None = True) -> Question:
        """Attach question to the lesson if selected"""
        instance = super().save(commit=False)

        if self.cleaned_data.get("lesson"):
            lesson = self.cleaned_data["lesson"]

            if commit:
                instance.save()
                # After saving, update the lesson to point to this question
                Lesson.objects.filter(question=self.instance).update(question=None)  # TODO: auditlog it
                lesson.question = instance
                lesson.save()

        if commit:
            instance.save()
            self.save_m2m()

        return instance


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = [
        "name",
        "courses_list",
    ]
    fields = [
        "courses",
        "course",
        "module",
        "lesson",
        "name",
        "deadline",
        "text",
    ]
    actions = [
        "dispatch_crosscheck",
    ]
    save_as = True
    form = QuestionForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        return super().get_queryset(request).for_admin()  # type: ignore

    def courses_list(self, question: Question) -> str:
        return ", ".join([course.name for course in question.courses.all()])

    @admin.action(description=_("Dispatch crosscheck"))
    def dispatch_crosscheck(self, request: Request, queryset: QuerySet) -> None:
        for question in queryset.iterator():
            tasks.dispatch_crosscheck.delay(question_id=question.id)

        self.message_user(request, f"Crosscheck dispatched for {queryset.count()} questions")
