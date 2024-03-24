from django.contrib import messages
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.forms import Media
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from rest_framework.request import Request

from apps.orders import human_readable
from apps.orders.admin.orders import actions
from apps.orders.admin.orders.filters import OrderStatusFilter
from apps.orders.admin.orders.forms import OrderAddForm, OrderChangeForm, OrderRefundForm
from apps.orders.admin.orders.throttling import OrderRefundActionThrottle
from apps.orders.admin.refunds.admin import RefundInline
from apps.orders.models import Order
from apps.orders.services import OrderRefunder
from apps.users.models import Student
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
        actions.refund,
        actions.ship_again_if_paid,
        actions.accept_homework,
        actions.disaccept_homework,
        actions.generate_diplomas,
    ]
    readonly_fields = [
        "author",
        "login_as",
        "paid",
        "shipped",
        "unpaid",
        "available_to_refund_amount",
    ]

    fieldsets = [
        (
            None,
            {
                "fields": ["user", "course", "price", "email", "author", "login_as", "paid", "shipped", "unpaid", "available_to_refund_amount"],
            },
        ),
    ]
    inlines = [RefundInline]
    change_form_template = "admin/order_changeform.html"

    def get_urls(self) -> list:
        urls = super().get_urls()
        custom_urls = [
            path("<path:pk>/partial_refund/", self.partial_refund, name="partial_refund"),
        ]
        return custom_urls + urls

    def response_change(self, request: "HttpRequest", obj: "Order") -> HttpResponse:
        if "_partial_refund" in request.POST:
            throttle = OrderRefundActionThrottle()
            if not throttle.allow_request(request, view=self):  # type: ignore
                self.message_user(
                    request,
                    _("Order can not be refunded. Up to 5 refunds per day are allowed. Please come back tomorrow."),
                    level=messages.ERROR,
                )
                return redirect(".")
            redirect_url = reverse("admin:partial_refund", args=(obj.pk,), current_app=self.admin_site.name)
            return HttpResponseRedirect(redirect_url)
        return super().response_change(request, obj)

    @atomic
    def partial_refund(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj = get_object_or_404(self.model, pk=pk)
        if request.method == "POST":
            form = OrderRefundForm(request.POST)
            if form.is_valid():
                OrderRefunder(
                    order=obj,
                    amount=form.cleaned_data["amount"],
                )()
                messages.success(request, _("Order is refunded"))
                return redirect("..")

        form = OrderRefundForm()
        return render(
            request,
            "admin/partial_refund.html",
            {
                "form": form,
                "title": _("Partial refund"),
                "help_text": _("You can refund up to"),
                "available_to_refund_amount": self.available_to_refund_amount(obj=obj),
            },
        )

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

        login_as_url = Student.objects.get(pk=obj.user_id).get_absolute_url()

        return f'<a href="{login_as_url}" target="_blank">Зайти</a>'

    @admin.display(description=_("Available to refund amount"))
    def available_to_refund_amount(self, obj: Order) -> str:
        return format_price(Order.objects.with_available_to_refund_amount().get(pk=obj.pk).available_to_refund_amount)

    def has_pay_permission(self, request: Request) -> bool:
        return request.user.has_perm("orders.pay_order")

    def has_unpay_permission(self, request: Request) -> bool:
        return request.user.has_perm("orders.unpay_order")
