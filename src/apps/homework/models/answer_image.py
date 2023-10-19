from app.files import RandomFileName
from app.models import models
from app.models import TimestampedModel


class AnswerImage(TimestampedModel):
    author = models.ForeignKey("users.User", on_delete=models.PROTECT)
    image = models.ImageField(upload_to=RandomFileName("homework/answers"))


__all__ = [
    "AnswerImage",
]
