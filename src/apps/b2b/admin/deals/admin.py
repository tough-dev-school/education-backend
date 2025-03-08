from apps.b2b.admin.deals import actions
from apps.b2b.admin.deals.forms import DealChangeForm, DealCreateForm
from apps.b2b.admin.students import StudentInline
from apps.b2b.models import Deal
from core.admin import ModelAdmin, admin


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    fields = [
        "author",
        "customer",
        "course",
        "price",
        "comment",
        "students",
    ]
    add_form = DealCreateForm
    form = DealChangeForm
    readonly_fields = [
        "author",
    ]
    inlines = [StudentInline]
    actions = [
        actions.complete,
        actions.ship_without_payment,
        actions.cancel,
    ]
