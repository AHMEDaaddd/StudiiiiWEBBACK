from rest_framework import serializers
from .models import User, Payment
from lms.serializers import LessonSerializer, CourseSerializer  # для вложенных ссылок (read-only отображение)


class PaymentSerializer(serializers.ModelSerializer):
    # Для удобства можно показать краткую информацию по связанным объектам (read-only)
    course_title = serializers.CharField(source="course.title", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "paid_at",
            "course",
            "course_title",
            "lesson",
            "lesson_title",
            "amount",
            "method",
        ]

    def validate(self, attrs):
        """
        Ровно одно из полей course/lesson должно быть заполнено.
        """
        course = attrs.get("course")
        lesson = attrs.get("lesson")
        if (course and lesson) or (not course and not lesson):
            raise serializers.ValidationError(
                "Нужно указать либо оплаченный курс, либо оплаченный урок (ровно одно из полей)."
            )
        return attrs


class UserSerializer(serializers.ModelSerializer):
    # Доп. задание: история платежей пользователя (read-only)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "city",
            "avatar",
            "first_name",
            "last_name",
            "payments",  # ← доп. задание (*)
        ]