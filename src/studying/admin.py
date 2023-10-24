from django.contrib import admin

from studying.models import Study


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    ...
