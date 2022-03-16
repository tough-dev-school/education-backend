from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models


class Chain(TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)


class Message(TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    chain = models.ForeignKey('chains.Chain', on_delete=models.CASCADE)
    template_id = models.CharField(max_length=256)

    parent = models.ForeignKey('chains.Message', on_delete=models.SET_NULL, null=True)
    delay = models.BigIntegerField(_('Delay (minutes)'), default=0)


class Progress(TimestampedModel):
    study = models.ForeignKey('studying.Study', on_delete=models.CASCADE)
    message = models.ForeignKey('chains.Message', on_delete=models.CASCADE)
