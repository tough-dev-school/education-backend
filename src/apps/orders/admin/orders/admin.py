from typing import Any

from django.db.models import ForeignKey, QuerySet
from django.forms.models import ModelChoiceField
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from rest_framework.request import Request

from apps.orders import human_readable
from apps.orders.admin.orders import actions
from apps.orders.admin.orders.filters import OrderStatusFilter
from apps.orders.admin.orders.forms import OrderAddForm, OrderChangeForm
from apps.orders.admin.refunds.admin import RefundInline
from apps.orders.models import Order
from apps.products.admin.filters import CourseFilter
from apps.products.models import Course
from apps.users.models import AdminUserProxy
from core.admin import ModelAdmin, admin
from core.pricing import format_price


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    form = OrderChangeForm
    add_form = OrderAddForm
    list_display = [
        "date",
        "customer",
        "item",
        "formatted_price",
        "payment",
        "promocode",
    ]
    list_display_links = [
        "date",
    ]

    list_filter = [
        OrderStatusFilter,
        CourseFilter,
    ]
    search_fields = [
        "course__name",
        "record__course__name",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]
    actions = [
        actions.set_paid,
        actions.ship_without_payment,
        actions.refund,
        actions.ship_again_if_paid,
        actions.accept_homework,
        actions.disaccept_homework,
        actions.generate_diplomas,
    ]
    readonly_fields = [
        "author",
        "deal",
        "email",
        "login_as",
        "paid",
        "shipped",
    ]

    fieldsets = [
        (
            None,
            {
                "fields": ["user", "email", "course", "price", "deal", "author", "login_as", "paid", "shipped", "bank_id"],
            },
        ),
    ]

    class Media:
        css = {"all": ["admin/order_list.css"]}
        js = ["admin/js/vendor/jquery/jquery.js", "admin/check_partial_refunds.js"]

    def get_queryset(self, request: Request) -> QuerySet:  # type: ignore
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
                "record",
                "course",
            )
        )

    def formfield_for_foreignkey(self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any) -> ModelChoiceField:
        if str(db_field) == "orders.Order.course" and request.method == "GET":
            if "add" in request.path:
                kwargs["queryset"] = Course.objects.for_admin()
            else:
                kwargs["queryset"] = Course.objects.select_related("group")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description=_("email"))
    def email(self, obj: Order) -> str:
        return obj.user.email

    @admin.display(description=_("Price"), ordering="price")
    def formatted_price(self, obj: Order) -> str:
        return format_price(obj.price)

    @admin.display(description=_("Date"), ordering="created")
    def date(self, obj: Order) -> str:
        return obj.created.strftime("%d.%m.%Y")

    @admin.display(description=_("User"), ordering="user__id")
    def customer(self, obj: Order) -> str:
        return human_readable.get_order_customer(obj)

    @admin.display(description=_("Item"))
    def item(self, obj: Order) -> str:
        return obj.item.name if obj.item is not None else "—"

    @admin.display(description=_("Payment"), ordering="paid")
    def payment(self, obj: Order) -> str:
        return human_readable.get_order_payment_method_name(obj)

    @admin.display(description=_("Login as customer"))
    @mark_safe
    def login_as(self, obj: Order) -> str:
        if obj.pk is None:
            return "—"  # type: ignore

        login_as_url = AdminUserProxy.objects.get(pk=obj.user_id).get_absolute_url()

        return f'<a href="{login_as_url}" target="_blank">Зайти</a>'

    def has_pay_permission(self, request: Request) -> bool:
        return request.user.has_perm("orders.pay_order")

    def has_unpay_permission(self, request: Request) -> bool:
        return request.user.has_perm("orders.unpay_order")

    def get_inlines(self, request: Request, obj: "Order | None") -> list:  # type: ignore
        if obj and obj.paid:
            return [RefundInline]
        return []
