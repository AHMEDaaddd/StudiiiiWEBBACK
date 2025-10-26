from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомный юзер с авторизацией по email.
    username остаётся как обязательное поле (для простоты), но логинимся по email.
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # при createsuperuser спросит username дополнительно

    def __str__(self):
        return self.email or self.username