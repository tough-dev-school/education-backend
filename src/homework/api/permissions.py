from rest_framework.permissions import BasePermission


class ShouldHavePurchasedCoursePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.course.get_purchased_users().filter(id=request.user.id).exists()
