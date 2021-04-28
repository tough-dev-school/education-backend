from django import forms
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from app.admin import admin
from users.creator import UserCreator
from users.models import User

admin.site.unregister(Group)


class PasswordLessUserCreationForm(forms.ModelForm):
    email = forms.CharField()

    class Meta:
        model = User
        fields = [
            'email',
        ]

    def save_m2m(self, *args, **kwargs):
        pass

    def save(self, commit=True):
        return UserCreator(name='', email=self.cleaned_data['email'])()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = PasswordLessUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                'fields': ['email'],
            },
        ),
    )


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass
