from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from apps.homework.models import AnswerAttachment


class AnswerAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerAttachment
        fields = [
            "id",
            "file",
            "created",
        ]


class AnswerAttachmentUploadSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf"])])

    class Meta:
        model = AnswerAttachment
        fields = [
            "author",
            "file",
        ]
