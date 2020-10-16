from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, admin
from courses.admin.courses import actions
from courses.admin.courses.record import RecordAdmin
from courses.models import Course


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fieldsets = [
        (_('Name'), {'fields': [
            'name',
            'name_genitive',
            'name_receipt',
            'full_name',
        ]}),
        (_('Price'), {'fields': [
            'price',
            'old_price',
        ]}),
        (_('Access'), {'fields': [
            'slug',
            'clickmeeting_room_url',
            'zoomus_webinar_id',
            'welcome_letter_template_id',
        ]}),
    ]

    list_display = [
        'id',
        'name',
        'slug',
    ]

    list_display_links = [
        'id',
        'name',
    ]

    prepopulated_fields = {
        'slug': ['name'],
    }
    inlines = [
        RecordAdmin,
    ]
    action_form = actions.CourseActionForm

    actions = [
        actions.send_email_to_all_purchased_users,
    ]
