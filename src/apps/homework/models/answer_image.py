from core.files import RandomFileName
from core.models import models
from core.models import TimestampedModel


class AnswerImage(TimestampedModel):
    author = models.ForeignKey("users.User", on_delete=models.PROTECT)
    image = models.ImageField(upload_to=RandomFileName("homework/answers"))


__all__ = [
    "AnswerImage",
]
