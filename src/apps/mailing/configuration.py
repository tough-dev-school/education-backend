from typing import TYPE_CHECKING, Optional  # NOQA: I251

from django.apps import apps

if TYPE_CHECKING:
    from apps.mailing.models import EmailConfiguration
    from apps.products.models import Course


def get_configuration(*, recipient: str) -> Optional["EmailConfiguration"]:
    """Find email conifguration by email taking it from the course the user has last contacted with"""
    last_contacted_course = get_last_contacted_course(recipient)

    if last_contacted_course is not None and hasattr(last_contacted_course, "email_configuration"):
        return last_contacted_course.email_configuration


def get_last_contacted_course(recipient: str) -> Optional["Course"]:
    last_order = apps.get_model("orders.Order").objects.filter(course__isnull=False, user__email=recipient).order_by("-created").first()

    if last_order is not None:
        return last_order.course


__all__ = [
    "get_configuration",
]
