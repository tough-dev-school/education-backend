from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from app.models import TimestampedModel, models
from app.pricing import format_old_price, format_price
from app.s3 import AppS3
from shipping import factory as ShippingFactory


class Shippable(TimestampedModel):
    """Add this to every shippable item"""
    name = models.CharField(max_length=255)
    name_receipt = models.CharField(_('Name for receipts'), max_length=255, help_text='«посещение мастер-класса по TDD» или «Доступ к записи курсов кройки и шитья»')
    full_name = models.CharField(
        _('Full name for letters'), max_length=255,
        help_text='Билет на мастер-класс о TDD или «запись курсов кройки и шитья»',
    )
    slug = models.SlugField()

    price = models.DecimalField(max_digits=8, decimal_places=2)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        abstract = True

    def get_price_display(self):
        return format_price(self.price)

    def get_old_price_display(self):
        return format_price(self.old_price)

    def get_formatted_price_display(self):
        return format_old_price(self.old_price, self.price)

    def ship(self, to):
        return ShippingFactory.ship(self, to=to)

    def get_template_id(self):
        """Get custom per-item template_id"""
        if not hasattr(self, 'template_id'):
            return

        if self.template_id is not None and len(self.template_id):
            return self.template_id


class Course(Shippable):
    name_genitive = models.CharField(_('Genitive name'), max_length=255, help_text='«мастер-класса о TDD». К примеру для записей.')
    clickmeeting_room_url = models.URLField(_('Clickmeeting room URL'), null=True, blank=True, help_text=_('If set, every user who purcashes this course gets invited'))
    template_id = models.CharField(_('Mailjet template_id'), max_length=256, blank=True, null=True, help_text=_('Leave it blank for the default template'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['courses', self.slug, '']))


class Record(Shippable):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    s3_object_id = models.CharField(max_length=512)
    template_id = models.CharField(_('Mailjet template_id'), max_length=256, blank=True, null=True, help_text=_('Leave it blank for the default template'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Record')
        verbose_name_plural = _('Records')

    @property
    def name_genitive(self):
        return self.course.name_genitive

    def get_url(self, expires: int = 3 * 24 * 60 * 60):
        return AppS3().get_presigned_url(self.s3_object_id, expires=expires)

    def __str__(self):
        return f'Запись {self.name_genitive}'

    def get_absolute_url(self):
        return self.course.get_absolute_url()


class Bundle(Shippable):
    records = models.ManyToManyField('courses.Record')
    courses = models.ManyToManyField('courses.Course')

    class Meta:
        ordering = ['-id']
        verbose_name = _('Bundle')
        verbose_name_plural = _('Bundles')

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['bundles', self.slug, '']))

    def ship(self, to):
        for record in self.records.iterator():
            record.ship(to=to)

        for course in self.courses.iterator():
            course.ship(to=to)
