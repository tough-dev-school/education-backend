from rest_framework.request import Request

from django.db.models import QuerySet
from django.forms import Media
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from app.admin import admin
from app.admin import ModelAdmin
from app.pricing import format_price
from orders.admin.orders import actions
from orders.admin.orders.filters import OrderStatusFilter
from orders.admin.orders.forms import OrderAddForm
from orders.admin.orders.forms import OrderChangeForm
from orders.models import HumanReadableOrder
from users.models import Student


@admin.register(HumanReadableOrder)
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
        "course",
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
        actions.set_not_paid,
        actions.ship_again_if_paid,
        actions.accept_homework,
        actions.disaccept_homework,
        actions.generate_diplomas,
    ]
    readonly_fields = [
        "slug",
        "author",
        "login_as",
        "paid",
        "shipped",
        "unpaid",
    ]

    fieldsets = [
        (
            None,
            {
                "fields": ["slug", "user", "price", "email", "author", "login_as", "paid", "shipped", "unpaid"],
            },
        ),
        (
            _("Item"),
            {
                "fields": ["course", "record", "bundle"],
            },
        ),
    ]

    @property
    def media(self) -> Media:
        media = super().media

        media._css_lists.append({"all": ["admin/order_list.css"]})  # type: ignore

        return media

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

    @admin.display(description=_("Price"), ordering="price")
    def formatted_price(self, obj: HumanReadableOrder) -> str:
        return format_price(obj.price)

    @admin.display(description=_("Date"), ordering="created")
    def date(self, obj: HumanReadableOrder) -> str:
        return obj.created.strftime("%d.%m.%Y")

    @admin.display(description=_("User"), ordering="user__id")
    def customer(self, obj: HumanReadableOrder) -> str:
        return obj.readable_customer

    @admin.display(description=_("Item"))
    def item(self, obj: HumanReadableOrder) -> str:
        return obj.item.name if obj.item is not None else "—"

    @admin.display(description=_("Payment"), ordering="paid")
    def payment(self, obj: HumanReadableOrder) -> str:
        return obj.readable_payment_method_name

    @admin.display(description=_("Login as customer"))
    @mark_safe
    def login_as(self, obj: HumanReadableOrder) -> str:
        if obj.pk is None:
            return "—"  # type: ignore

        login_as_url = Student.objects.get(pk=obj.user_id).get_absolute_url()

        return f'<a href="{login_as_url}" target="_blank">Зайти от имени студента</a>'

    def has_pay_permission(self, request: Request) -> bool:
        return request.user.has_perm("orders.pay_order")

    def has_unpay_permission(self, request: Request) -> bool:
        return request.user.has_perm("orders.unpay_order")
