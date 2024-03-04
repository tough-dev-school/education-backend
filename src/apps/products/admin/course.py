from typing import Any

from django.http import HttpRequest
from django.utils.translation import gettext as _

from apps.amocrm import tasks
from apps.mailing.admin.email_configuration import EmailConfigurationAdmin
from apps.products.admin.courses import actions
from apps.products.models import Course
from core.admin import ModelAdmin, admin


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fieldsets = [
        (
            _("Name"),
            {
                "fields": [
                    "name",
                    "slug",
                    "cover",
                    "display_in_lms",
                    "disable_triggers",
                    "group",
                    "name_genitive",
                    "name_receipt",
                    "full_name",
                    "name_international",
                ],
            },
        ),
        (
            _("Price"),
            {
                "fields": [
                    "price",
                    "old_price",
                ],
            },
        ),
        (
            _("Email messages"),
            {
                "fields": [
                    "welcome_letter_template_id",
                    "diploma_template_context",
                ],
            },
        ),
        (
            _("Order confirmation"),
            {
                "fields": [
                    "confirmation_template_id",
                    "confirmation_success_url",
                ],
            },
        ),
    ]

    list_display = (
        "id",
        "group",
        "name",
        "slug",
        "has_cover",
    )

    list_filter = ("group",)

    list_display_links = (
        "id",
        "name",
    )

    prepopulated_fields = {
        "slug": ["name"],
    }
    inlines = (EmailConfigurationAdmin,)
    action_form = actions.CourseActionForm

    actions = [
        actions.send_email_to_all_purchased_users,
        actions.generate_deplomas_for_all_purchased_users,
    ]

    save_as = True
    search_fields = ("name",)

    @admin.display(boolean=True)
    def has_cover(self, course: Course) -> bool:
        return bool(course.cover)

    def save_model(self, request: HttpRequest, obj: Course, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)

        if tasks.amocrm_enabled():
            tasks.push_course.apply_async(kwargs={"course_id": obj.pk}, countdown=1)
