from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Кастомный юзер с авторизацией по email.
    """

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email or self.username


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счёт"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="пользователь",
    )
    paid_at = models.DateTimeField(default=timezone.now, verbose_name="дата оплаты")

    # Оплата либо за курс, либо за урок
    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name="оплаченный курс",
    )
    lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name="оплаченный урок",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="сумма оплаты",
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.TRANSFER,
        verbose_name="способ оплаты",
    )

    class Meta:
        ordering = ["-paid_at"]
        verbose_name = "платёж"
        verbose_name_plural = "платежи"

    def __str__(self):
        target = self.course or self.lesson
        return f"Платёж {self.id} от {self.user} за {target} на {self.amount} ({self.get_method_display()})"
