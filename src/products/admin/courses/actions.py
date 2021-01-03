from django import forms
from django.contrib.admin.helpers import ActionForm
from django.utils.translation import gettext_lazy as _


class CourseActionForm(ActionForm):
    template_id = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': _('Email template id')}),
        max_length=32,
    )

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js', 'js/admin/course_action_form.js')
        css = {
            'all': ['css/admin/course_action_form.css'],
        }


def send_email_to_all_purchased_users(modeladmin, request, queryset):
    course_count = 0
    purchased_users_count = 0

    for course in queryset.iterator():
        course.send_email_to_all_purchased_users(template_id=request.POST['template_id'])

        course_count += 1
        purchased_users_count += course.get_purchased_users().count()

    modeladmin.message_user(request, f'Sending letter to {purchased_users_count} customers of {course_count} courses')


send_email_to_all_purchased_users.short_description = _('Send email to all purchased_users')
