from django import forms
from django.contrib.admin.models import CHANGE
from django.utils.translation import gettext_lazy as _

from apps.homework.models import Question
from apps.lms.models import Lesson, Module
from core.admin.forms import ModelForm
from core.current_user import get_current_user
from core.tasks import write_admin_log


class QuestionForm(ModelForm):
    module = forms.ModelChoiceField(label=_("Module"), queryset=Module.objects.for_admin().exclude(archived=True), required=False)
    lesson = forms.ModelChoiceField(label=_("Lesson"), queryset=Lesson.objects.for_admin(), required=False)

    class Meta:
        model = Question
        fields = [
            "name",
            "deadline",
            "module",
            "lesson",
            "text",
        ]

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/limit_module_choices.js",
        )

    def get_custom_initial_data(self, question: Question) -> dict[str, str]:  # type: ignore
        lesson = Lesson.objects.filter(question=question).select_related("module").first()
        if lesson:
            return {"lesson": lesson.pk, "module": lesson.module_id, "course": lesson.module.course_id}

        return {}

    def save(self, commit: bool = True) -> Question:
        """Attach question to the lesson if selected"""
        instance = super().save(commit=commit)

        if self.cleaned_data.get("lesson"):
            lesson = self.cleaned_data["lesson"]

            self._detach_all_other_lessons(question=self.instance)
            self._update_question(lesson, question=self.instance)
            self._write_admin_log(lesson, msg=f"Question '{self.instance}' attached to the lesson")

        return instance

    @classmethod
    def _detach_all_other_lessons(cls, question: Question) -> None:
        if question is not None and question.pk is None:  # handle 'save as new' functionality
            return None  # type: ignore [unreachable]

        for lesson in Lesson.objects.filter(question=question).iterator():
            cls._update_question(lesson, question=None)
            cls._write_admin_log(lesson, msg=f"Question '{question.name}' (#{question.pk}) detached from the lesson")

    @staticmethod
    def _update_question(lesson: Lesson, question: Question | None = None) -> None:
        if question is not None and question.pk is None:  # handle 'save as new' functionality
            return None  # type: ignore [unreachable]
        lesson.question = question
        lesson.save(update_fields=["modified", "question"])

    @staticmethod
    def _write_admin_log(lesson: Lesson, msg: str) -> None:
        user = get_current_user()
        if user is None:
            raise RuntimeError("Cannot determine user")

        write_admin_log.delay(
            action_flag=CHANGE,
            change_message=msg,
            model="lms.Lesson",
            object_id=lesson.pk,
            user_id=user.id,
        )
