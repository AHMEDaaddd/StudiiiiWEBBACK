from django.urls import path

from .views import (CourseSubscriptionAPIView, LessonListCreateAPIView,
                    LessonRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-detail",
    ),
    path(
        "courses/<int:course_id>/subscription/",
        CourseSubscriptionAPIView.as_view(),
        name="course-subscription",
    ),
]
