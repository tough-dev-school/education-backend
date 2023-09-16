from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import OuterRef
from django.db.models import QuerySet
from django.db.models import Subquery
from django.utils.translation import gettext_lazy as _

from app.files import RandomFileName
from app.models import models
from mailing.tasks import send_mail
from products.models.base import Shippable
from users.models import User


class CourseQuerySet(QuerySet):
    def for_lms(self) -> QuerySet["Course"]:
        return self.filter(
            display_in_lms=True,
        ).with_course_homepage()

    def with_course_homepage(self) -> QuerySet["Course"]:
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
        name = getattr(self, "name", None)
        group = getattr(self, "group", None)
        if name is not None and group is not None:
            return f"{name} - {group.name}"

        return super().__str__()
