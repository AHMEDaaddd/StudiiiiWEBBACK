from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

# --- КУРСЫ: ViewSet (CRUD) ---
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer

# --- УРОКИ: Generic (CRUD) ---
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer

class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer