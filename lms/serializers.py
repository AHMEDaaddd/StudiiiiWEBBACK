from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url
from .models import Course, Lesson, Subscription

class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
        validators=[validate_youtube_url],
    )

    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "description", "preview", "video_url"]

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "preview", "description", "lessons_count", "is_subscribed"]

    def get_is_subscribed(self, obj) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, course=obj).exists()