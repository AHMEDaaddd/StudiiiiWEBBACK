from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    Доп.задание: CRUD для профилей пользователей.
    На этапе ДЗ доступ открыт всем (AllowAny в настройках DRF).
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer