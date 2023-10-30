from typing import Any

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.utils.functional import cached_property

from app.current_user import get_current_user
from products.models import Course
from users.api.serializers import CourseStudentSerializer
from users.api.serializers import UserSerializer
from users.models import User
from users.services import UserUpdater


class SelfView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        user_updater = UserUpdater(
            user=self.get_object(),
            user_data=request.data,
        )

        user = user_updater()

        return Response(
            self.get_serializer(user).data,
        )

    def get_object(self) -> User:
        user = get_current_user()
        if user is not None:
            return self.get_queryset().get(pk=user.pk)

        raise ImproperlyConfigured("This code should not be ran")

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.filter(is_active=True)


class CourseStudentViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (IsAdminUser,)
    serializer_class = CourseStudentSerializer

    @cached_property
    def course(self) -> "Course":
        id = self.request.query_params.get("course")

        return get_object_or_404(Course, id=id)

    def get_queryset(self) -> "QuerySet[User]":
        return self.course.get_purchased_users().order_by("first_name", "last_name")
