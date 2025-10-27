from rest_framework import viewsets
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer
from .filters import PaymentFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD профилей пользователей (как в доп. задании прошлого ДЗ).
    AllowAny — по условиям курса на этом этапе.
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Список/детально платежей с фильтрацией и сортировкой.
    Сортировка: ?ordering=paid_at или ?ordering=-paid_at
    Фильтры: ?course=ID, ?lesson=ID, ?method=cash|transfer
             (дополнительно: ?paid_at__gte=ISO, ?paid_at__lte=ISO)
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