from decimal import Decimal
from django.db.models import Case, Count, When
from django.utils.translation import gettext_lazy as _

from app.models import DefaultQuerySet, TimestampedModel, models
from products.models import Course


class PromoCodeQuerySet(DefaultQuerySet):
    def active(self):
        return self.filter(active=True)

    def with_order_count(self):
        return self.annotate(order_count=Count(Case(
            When(order__paid__isnull=False, then=1),
            output_field=models.IntegerField(),
        )))

    def get_or_nothing(self, name):
        try:
            return self.active().get(name__iexact=name)

        except PromoCode.DoesNotExist:
            return None


class PromoCode(TimestampedModel):
    objects = PromoCodeQuerySet.as_manager()

    name = models.CharField(_('Promo Code'), max_length=32, unique=True, db_index=True)
    discount_percent = models.IntegerField(_('Discount percent'))
    active = models.BooleanField(_('Active'), default=True)
    comment = models.TextField(_('Comment'), blank=True, null=True)

    courses = models.ManyToManyField('products.Course', help_text=_('Can not be used for courses not checked here'))

    class Meta:
        verbose_name = _('Promo Code')
        verbose_name_plural = _('Promo Codes')

    def compatible_with(self, course: Course) -> bool:
        return self.courses.count() == 0 or course in self.courses.all()

    def apply(self, price: Decimal) -> Decimal:
        return Decimal(price * (100 - self.discount_percent) / 100)
