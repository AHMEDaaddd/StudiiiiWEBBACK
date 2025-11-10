from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to="courses/", blank=True, null=True)
    description = models.TextField(blank=True)
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
