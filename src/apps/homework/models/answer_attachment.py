from core.files import RandomFileName
from core.models import TimestampedModel, models


class AnswerAttachment(TimestampedModel):
    author = models.ForeignKey("users.User", on_delete=models.PROTECT)
    file = models.FileField(upload_to=RandomFileName("homework/attachments"))


__all__ = [
    "AnswerAttachment",
]
