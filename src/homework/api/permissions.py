from rest_framework.permissions import BasePermission
from django.conf import settings

class ShouldHavePurchasedCoursePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING or obj.course.get_purchased_users().filter(id=request.user.id).exists()


class ShouldHavePurchasedQuestionCoursePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING or obj.question.course.get_purchased_users().filter(id=request.user.id).exists()
