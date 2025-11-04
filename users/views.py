from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, Payment
from .serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserRegistrationSerializer,
    PaymentSerializer,
)
from .filters import PaymentFilter
from .permissions import IsSelf


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD профилей пользователей.

    - POST /api/users/  — регистрация (AllowAny)
    - GET /api/users/   — список публичных профилей (только авторизованные)
    - GET /api/users/{id}/ — любой авторизованный, но:
        * свой профиль — детальный (с платежами, фамилией)
        * чужой профиль — только публичные поля
    - PUT/PATCH/DELETE — только владелец своего профиля.
    """
    queryset = User.objects.all().order_by("id")

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsSelf]
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action == "list":
            return UserPublicSerializer
        if self.action == "retrieve":
            # если пользователь запрашивает сам себя — детальный
            request_user = self.request.user
            if request_user.is_authenticated and str(request_user.pk) == str(self.kwargs.get("pk")):
                return UserSerializer
            return UserPublicSerializer
        # обновление/удаление — всегда детальный (но IsSelf ограничит доступ)
        return UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Список/детально платежей с фильтрацией и сортировкой.
    Доступ только для авторизованных пользователей.
    """
    queryset = (
        Payment.objects
        .select_related("user", "course", "lesson")
        .all()
    )
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ["paid_at", "amount"]
    search_fields = ["user__email", "course__title", "lesson__title"]
    permission_classes = [IsAuthenticated]