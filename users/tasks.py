from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone


@shared_task
def deactivate_inactive_users_task() -> int:
    """
    Периодическая задача для Celery.

    Блокирует (is_active=False) пользователей, которые не заходили
    в систему более 30 дней (по полю last_login).
    Запускается по расписанию через celery-beat.
    """
    User = get_user_model()
    now = timezone.now()
    threshold = now - timedelta(days=30)

    # last_login старше месяца (и не None) и пользователь активен
    qs = User.objects.filter(is_active=True, last_login__lt=threshold)
    updated = qs.update(is_active=False)

    return updated