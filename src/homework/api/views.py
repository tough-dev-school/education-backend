from rest_framework.generics import RetrieveAPIView

from homework.api.permissions import ShouldHavePurchasedCoursePermission
from homework.api.serializers import QuestionSerializer
from homework.models import Question


class QuestionView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [ShouldHavePurchasedCoursePermission]
    lookup_field = 'slug'
