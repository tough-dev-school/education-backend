from datetime import timedelta

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Q, QuerySet, Subquery
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.mailing.tasks import send_mail
from apps.products.models.base import Shippable
from apps.users.models import User
from core.files import RandomFileName
from core.models import models


class CourseQuerySet(QuerySet):
    def for_lms(self) -> "CourseQuerySet":
        return self.filter(
            display_in_lms=True,
        ).with_course_homepage()

    def with_course_homepage(self) -> "CourseQuerySet":
        materials = (
            apps.get_model("notion.Material")
            .objects.filter(
                course=OuterRef("pk"),
                is_home_page=True,
            )
            .order_by(
                "-created",
            )
            .values(
                "page_id",
            )
        )

        return self.annotate(
            home_page_slug=Subquery(materials[:1]),
        )

    def for_admin(self) -> "CourseQuerySet":
        return self.select_related("group").filter(Q(group__created__gte=timezone.now() - timedelta(days=365)) | Q(group__evergreen=True))

    def purchased_by(self, user: User) -> "CourseQuerySet":
        return self.filter(
            id__in=apps.get_model("studying.Study").objects.filter(student=user).values("course"),
        )


CourseManager = models.Manager.from_queryset(CourseQuerySet)


class Course(Shippable):
    objects = CourseManager()

    name_genitive = models.CharField(_("Genitive name"), max_length=255, help_text="«мастер-класса о TDD». К примеру для записей.")

    welcome_letter_template_id = models.CharField(
        _("Welcome letter template id"), max_length=255, blank=True, null=True, help_text=_("Will be sent upon purchase if set")
    )
    display_in_lms = models.BooleanField(_("Display in LMS"), default=True, help_text=_("If disabled will not be shown in LMS"))

    diploma_template_context = models.JSONField(default=dict, blank=True)

    disable_triggers = models.BooleanField(_("Disable all triggers"), default=False)

    confirmation_template_id = models.CharField(
        _("Confirmation template id"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("If set user sill receive this message upon creating zero-priced order"),
    )
    confirmation_success_url = models.URLField(_("Confirmation success URL"), null=True, blank=True)

    calendar_google = models.URLField(_("Calendar URL (Google)"), blank=True, null=True)
    calendar_ios = models.URLField(_("Calendar URL (iOS)"), blank=True, null=True)

    chat = models.URLField(_("Chat URL"), blank=True, null=True)

    cover = models.ImageField(
        verbose_name=_("Cover image"),
        upload_to=RandomFileName("courses/covers"),
        blank=True,
        help_text=_("The cover image of course"),
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        db_table = "courses_course"

    def clean(self) -> None:
        """Check for correct setting of confirmation_template_id and confirmation_success_url"""
        if not self.confirmation_template_id and not self.confirmation_success_url:
            return

        if not all([self.confirmation_template_id, self.confirmation_success_url]):
            raise ValidationError(_("Both confirmation_template_id and confirmation_success_url must be set"))

        if self.price != 0:
            raise ValidationError(_("Courses with confirmation should have zero price"))

    def get_purchased_users(self) -> QuerySet[User]:
        return User.objects.filter(
            pk__in=apps.get_model("studying.Study").objects.filter(course=self).values_list("student", flat=True),
        )

    def send_email_to_all_purchased_users(self, template_id: str) -> None:
        for user in self.get_purchased_users().iterator():
            send_mail.delay(
                to=user.email,
                template_id=template_id,
            )

    def __str__(self) -> str:
        return f"{self.name} - {self.group.name}"
