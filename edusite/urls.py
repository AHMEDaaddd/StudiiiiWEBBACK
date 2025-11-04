from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from lms.views import CourseViewSet
from users.views import UserViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"users", UserViewSet, basename="user")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include("lms.urls")),

    # JWT-авторизация
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)