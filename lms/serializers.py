from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "description", "preview", "video_url"]

class CourseSerializer(serializers.ModelSerializer):
    # Задание 1: количество уроков через SerializerMethodField
    lessons_count = serializers.SerializerMethodField(read_only=True)
    # Задание 3: вложенный вывод уроков
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "preview", "description", "lessons_count", "lessons"]

    def get_lessons_count(self, obj) -> int:
        # избегаем лишних запросов при annotate; сейчас просто считаем
        return obj.lessons.count()