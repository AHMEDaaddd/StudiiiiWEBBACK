from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from lms.models import Course, Lesson, Subscription
from lms.paginators import CoursePagination, LessonPagination
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner


# --- КУРСЫ: ViewSet (CRUD) ---
@extend_schema(
    tags=["Courses"],
    summary="Управление курсами",
    description=(
        "Просмотр списка курсов, создание нового курса, "
        "получение, обновление и удаление конкретного курса."
    ),
)
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
@extend_schema(
    tags=["Lessons"],
    summary="Список уроков и создание урока",
    description=(
        "Возвращает список уроков текущего пользователя (модератор видит все уроки). "
        "Позволяет создавать новые уроки."
    ),
)
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


@extend_schema(
    tags=["Lessons"],
    summary="Просмотр, изменение и удаление урока",
    description=(
        "Возвращает данные урока по ID. "
        "Обновление и удаление разрешены владельцу или модератору."
    ),
)
class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class CourseSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Subscriptions"],
        summary="Подписка / отписка от обновлений курса",
        description=(
            "Тоггл-подписка на курс: если подписки нет — создаёт, "
            "если есть — удаляет. Возвращает текстовое сообщение."
        ),
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID курса, на который оформляется/снимается подписка",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Успешный ответ с полем "message" ("подписка добавлена" или "подписка удалена").'
            ),
            401: OpenApiResponse(description="Пользователь не авторизован"),
            404: OpenApiResponse(description="Курс не найден"),
        },
    )
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
