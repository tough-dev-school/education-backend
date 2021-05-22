from django.db.models import Index, UniqueConstraint

from app.models import TimestampedModel, models


class Study(TimestampedModel):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE)
    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            Index(fields=['student', 'course']),
        ]
        constraints = [
            UniqueConstraint(fields=['student', 'course'], name='unique_student_course_study'),
        ]
