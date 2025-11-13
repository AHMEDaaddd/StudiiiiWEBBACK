from django.conf import settings
from django.db import models




#from lms.models import Course  # если импорт именно так, оставляй; если ниже — адаптируй

class Course(models.Model):
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to="courses/", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
        verbose_name="владелец",
    )

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preview = models.ImageField(upload_to="lessons/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        null=True,
        blank=True,
        verbose_name="владелец",
    )

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Subscription(models.Model):
    """
    Подписка пользователя на обновления курса.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="курс",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата подписки",
    )

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "подписка на курс"
        verbose_name_plural = "подписки на курсы"

    def __str__(self) -> str:
        return f"{self.user} -> {self.course}"

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lms_payments",
        related_query_name="lms_payment",
    )
    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="lms_payments",
        related_query_name="lms_payment",
    )

    amount = models.DecimalField(max_digits=9, decimal_places=2)  # в единицах валюты (напр. 10.00)
    currency = models.CharField(max_length=10, default="usd")

    stripe_product_id = models.CharField(max_length=64, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=64, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=128, blank=True, null=True)
    stripe_checkout_url = models.URLField(blank=True, null=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.pk} {self.user} → {self.course} [{self.status}]"

    def __str__(self):
        return f"Payment #{self.pk} {self.user} → {self.course} [{self.status}]"