from urllib.parse import urlparse

from rest_framework import serializers


ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be"}


def validate_youtube_url(value: str):
    """
    Разрешаем только ссылки на youtube.com / youtu.be.
    Пустое значение — ок.
    """
    if not value:
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower()

    # возможный вариант: убрать порт, если есть
    if ":" in host:
        host = host.split(":", 1)[0]

    if host not in ALLOWED_HOSTS:
        raise serializers.ValidationError(
            "Разрешены только ссылки на Youtube (youtube.com / youtu.be)."
        )

    return value