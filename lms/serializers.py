from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "description", "preview", "video_url"]

class CourseSerializer(serializers.ModelSerializer):

    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "preview", "description", "lessons_count"]