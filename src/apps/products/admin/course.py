from typing import Any

from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy

from apps.amocrm import tasks
from apps.products.admin.courses import actions, inlines
from apps.products.models import Course
from core.admin import ModelAdmin, admin
from core.pricing import format_price


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fieldsets = [
        (
            _("Name"),
            {
                "fields": [
                    "name",
                    "slug",
                    "group",
                    "display_in_lms",
                    "disable_triggers",
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
            pgettext_lazy("products", "Invoices"),
            {
                "fields": [
                    "name_genitive",
                    "name_receipt",
                    "full_name",
                    "name_international",
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
        "formatted_price",
    )

    list_filter = ("group",)

    list_display_links = (
        "id",
        "name",
    )

    prepopulated_fields = {
        "slug": ["name"],
    }
    inlines = (
        inlines.EmailConfigurationAdmin,
        inlines.DiplomaTemplateAdmin,
    )
    action_form = actions.CourseActionForm

    actions = [
        actions.send_email_to_all_purchased_users,
        actions.generate_deplomas_for_all_purchased_users,
    ]

    save_as = True
    search_fields = ("name",)

    @admin.display(description=_("Price"), ordering="price")
    def formatted_price(self, course: Course) -> str:
        return format_price(course.price)

    def save_model(self, request: HttpRequest, obj: Course, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)

        if tasks.amocrm_enabled():
            tasks.push_course.apply_async(kwargs={"course_id": obj.pk}, countdown=1)
