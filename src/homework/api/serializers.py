from rest_framework import serializers

from app.serializers import MarkdownXField, SoftField
from homework.models import Answer, Question
from users.api.serializers import UserNameSerializer


class QuestionSerializer(serializers.ModelSerializer):
    text = MarkdownXField()

    class Meta:
        model = Question
        fields = [
            'slug',
            'name',
            'text',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()
    text = MarkdownXField()
    parent = SoftField(source='parent.slug')

    class Meta:
        model = Answer
        fields = [
            'created',
            'slug',
            'author',
            'parent',
            'text',
        ]


class AnswerRetrieveSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()
    text = MarkdownXField()
    parent = SoftField(source='parent.slug')
    descendants = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'created',
            'slug',
            'author',
            'parent',
            'text',
            'descendants',
        ]

    def get_descendants(self, obj):
        user = self.context['request'].user
        queryset = obj.get_first_level_descendants()
        if not user.has_perm('homework.see_all_answers'):
            queryset = queryset.for_user(user)

        serializer = AnswerRetrieveSerializer(
            queryset,
            many=True,
            context=self.context,
        )

        return serializer.data


class AnswerCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    parent = serializers.SlugRelatedField(slug_field='slug', queryset=Answer.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Answer
        fields = [
            'author',
            'question',
            'parent',
            'text',
        ]
