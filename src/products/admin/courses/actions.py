from django import forms
from django.contrib.admin import action
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


@action(description=_('Send email to all purchased_users'))
def send_email_to_all_purchased_users(modeladmin, request, queryset):
    course_count = 0
    purchased_users_count = 0

    for course in queryset.iterator():
        course.send_email_to_all_purchased_users(template_id=request.POST['template_id'])

        course_count += 1
        purchased_users_count += course.get_purchased_users().count()

    modeladmin.message_user(request, f'Sending letter to {purchased_users_count} customers of {course_count} courses')


@action(description=_('Generate diplomas'))
def generate_deplomas_for_all_purchased_users(modeladmin, request, queryset):
    course_count = 0
    purchased_users_count = 0
    templates_count = 0

    for course in queryset.iterator():
        course_count += 1
        purchased_users_count += course.get_purchased_users().count()

        for diploma_template in course.diplomatemplate_set.iterator():
            templates_count += 1
            for user in course.get_purchased_users().iterator():
                diploma_template.generate_diploma(user)
                purchased_users_count += 1

    modeladmin.message_user(request, f'Stared generation of {templates_count} diplomas for {purchased_users_count} customers of {course_count} courses')
