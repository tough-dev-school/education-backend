from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from mailing.admin.email_configuration import EmailConfigurationAdmin
from products.admin.courses import actions
from products.models import Course


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fieldsets = [
        (
            _('Name'),
            {
                'fields': [
                    'name',
                    'slug',
                    'display_in_lms',
                    'disable_triggers',
                    'group',
                    'name_genitive',
                    'name_receipt',
                    'full_name',
                    'name_international',
                ],
            },
        ),
        (
            _('Price'),
            {
                'fields': [
                    'price',
                    'old_price',
                ],
            },
        ),
        (
            _('Email messages'),
            {
                'fields': [
                    'welcome_letter_template_id',
                    'gift_welcome_letter_template_id',
                    'diploma_template_context',
                ],
            },
        ),
    ]

    list_display = (
        'id',
        'group',
        'name',
        'slug',
    )

    list_filter = (
        'group',
    )

    list_display_links = (
        'id',
        'name',
    )

    prepopulated_fields = {
        'slug': ['name'],
    }
    inlines = (
        EmailConfigurationAdmin,
    )
    action_form = actions.CourseActionForm

    actions = [
        actions.send_email_to_all_purchased_users,
        actions.generate_deplomas_for_all_purchased_users,
    ]

    save_as = True
