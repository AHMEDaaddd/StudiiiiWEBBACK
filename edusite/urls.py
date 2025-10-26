from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from .views import root_welcome

from lms.views import CourseViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", root_welcome),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include("lms.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)