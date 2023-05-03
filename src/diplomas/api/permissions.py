from rest_framework import permissions


class DiplomaPermission(permissions.DjangoObjectPermissions):
    """Allow every (even anonymous) user to access particular diplomas.
    Use default Django permissions for any other action
    """

    def has_permission(self, request, view):
        if view.action == "retrieve":
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_object_permission(request, view, obj)
