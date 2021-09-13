from django import forms
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

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
    list_display = ('email', 'first_name', 'last_name', 'gender')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'gender')}),
        (_('Name in english'), {'fields': ('first_name_en', 'last_name_en')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'order__study__course')
    list_editable = ('gender',)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass
