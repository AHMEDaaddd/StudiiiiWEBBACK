from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import CoursePagination, LessonPagination
from users.permissions import IsOwner, IsModer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Course, Subscription


# --- КУРСЫ: ViewSet (CRUD) ---
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_queryset(self):
        """
        Модератор (и staff/superuser) видит все курсы.
        Обычный пользователь — только свои.
        """
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()

        from users.permissions import is_moderator

        if is_moderator(user):
            return qs
        return qs.filter(owner=user)

    def perform_create(self, serializer):
        """
        При создании курса привязываем владельца.
        """
        serializer.save(owner=self.request.user)

    def get_permissions(self):

        if self.action == "create":
            permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ["list", "retrieve", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [perm() for perm in permission_classes]


# --- УРОКИ: Generic (CRUD) ---
class LessonListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPagination

    def get_queryset(self):
        """
        Модератор видит все уроки, обычный пользователь — только свои.
        """
        qs = Lesson.objects.all().order_by("id")
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()

        from users.permissions import is_moderator

        if is_moderator(user):
            return qs
        return qs.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):

        if self.request.method == "GET":
            permission_classes = [IsAuthenticated]  # фильтр по get_queryset
        elif self.request.method == "POST":
            permission_classes = [IsAuthenticated, ~IsModer]
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class CourseSubscriptionAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, course_id: int, *args, **kwargs):
        user = request.user

        # получаем курс по course_id из URL
        course = get_object_or_404(Course, pk=course_id)

        subs_qs = Subscription.objects.filter(user=user, course=course)

        if subs_qs.exists():
            subs_qs.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
