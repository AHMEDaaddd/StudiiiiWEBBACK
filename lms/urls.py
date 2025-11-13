from django.urls import path, include
from rest_framework.routers import DefaultRouter

from lms.views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
    CourseSubscriptionAPIView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("", include(router.urls)),

    # уроки
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonRetrieveUpdateDestroyAPIView.as_view(), name="lesson-detail"),

    # подписка
    path("courses/<int:course_id>/subscription/", CourseSubscriptionAPIView.as_view(),
         name="course-subscription"),
]