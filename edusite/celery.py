import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edusite.settings")

app = Celery("edusite")


app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически искать tasks.py во всех приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")