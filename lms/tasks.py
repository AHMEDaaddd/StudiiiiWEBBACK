from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from lms.models import Course, Lesson, Subscription


@shared_task
def send_course_update_email_task(course_id: int) -> int:
    """
    Асинхронно отправляет письма всем подписчикам курса.
    Ограничение: не чаще одного раза в 4 часа.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return 0

    now = timezone.now()
    last_sent = getattr(course, "last_notification_sent_at", None)

    # Ограничение: если уже рассылали < 4 часов назад — ничего не шлём
    if last_sent and now - last_sent < timedelta(hours=4):
        return 0

    subscriptions = (
        Subscription.objects
        .filter(course=course)
        .select_related("user")
    )
    recipients = [s.user.email for s in subscriptions if s.user.email]

    if not recipients:
        return 0

    subject = f"Обновление курса «{course.title}»"
    message = (
        f"Материалы курса «{course.title}» были обновлены.\n"
        f"Зайдите в личный кабинет, чтобы посмотреть изменения."
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    send_mail(
        subject,
        message,
        from_email,
        recipients,
        fail_silently=True,
    )

    course.last_notification_sent_at = now
    course.save(update_fields=["last_notification_sent_at"])

    return len(recipients)


@shared_task
def send_lesson_update_email_if_needed_task(lesson_id: int) -> int:
    """
    Доп. задание со звёздочкой.
    Пользователь может обновлять отдельный урок.
    Отправляем уведомление ТОЛЬКО если по курсу не было рассылки > 4 часов.

    По сути — тот же ограничитель, но триггерится обновлением урока.
    """
    try:
        lesson = Lesson.objects.select_related("course").get(pk=lesson_id)
    except Lesson.DoesNotExist:
        return 0

    course = lesson.course
    now = timezone.now()
    last_sent = getattr(course, "last_notification_sent_at", None)

    if last_sent and now - last_sent < timedelta(hours=4):
        # курс «считается» недавно обновлённым — не шлём
        return 0

    subscriptions = (
        Subscription.objects
        .filter(course=course)
        .select_related("user")
    )
    recipients = [s.user.email for s in subscriptions if s.user.email]

    if not recipients:
        return 0

    subject = f"Обновление урока «{lesson.title}» в курсе «{course.title}»"
    message = (
        f"В курсе «{course.title}» обновлён урок «{lesson.title}».\n"
        f"Зайдите в личный кабинет, чтобы ознакомиться с новыми материалами."
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    send_mail(
        subject,
        message,
        from_email,
        recipients,
        fail_silently=True,
    )

    course.last_notification_sent_at = now
    course.save(update_fields=["last_notification_sent_at"])

    return len(recipients)


@shared_task
def deactivate_inactive_users_task() -> int:
    """
    Задание 3.
    Блокирует (is_active=False) пользователей, которые не заходили более месяца.
    Запускается периодически через celery-beat.
    """
    User = get_user_model()
    now = timezone.now()
    threshold = now - timedelta(days=30)

    # last_login старше месяца (и не None) и пользователь активен
    qs = User.objects.filter(is_active=True, last_login__lt=threshold)
    updated = qs.update(is_active=False)

    return updated