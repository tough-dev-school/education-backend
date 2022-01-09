from django.db.models import QuerySet, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models


class MaterialQuerySet(QuerySet):
    def active(self) -> QuerySet['Material']:
        return self.filter(active=True)


class Material(TimestampedModel):
    objects = models.Manager.from_queryset(MaterialQuerySet)()

    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)
    page_id = models.CharField(_('Notion page id'), max_length=64, db_index=True, help_text=_('Paste it from notion address bar'))
    active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Notion material')
        verbose_name_plural = _('Notion materials')
        constraints = [
            UniqueConstraint(fields=['course', 'page_id'], name='single_page_per_single_course'),
        ]
        permissions = [
            ('see_all_materials', _('May access materials from every course')),
        ]
