from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models


class EmailConfiguration(TimestampedModel):
    """Configuration is the low-level database storage for email backend settings, e.g. mail_from, or raw backend kwargs
    """
    class BACKEND(models.TextChoices):
        UNSET = '', _('Unset')
        POSTMARK = 'anymail.backends.postmark.EmailBackend', _('Postmark')

    backend = models.CharField(max_length=256, choices=BACKEND.choices, default=BACKEND.UNSET)
    course = models.OneToOneField('products.Course', related_name='email_configuration', on_delete=models.CASCADE)
    email_from = models.CharField(_('Email sender'), max_length=256, help_text=_('E.g. Fedor Borshev <fedor@borshev.com>'))

    backend_options = models.JSONField(default=dict)

    class Meta:
        verbose_name = _('Email configuration')
        verbose_name_plural = _('Email configurations')
