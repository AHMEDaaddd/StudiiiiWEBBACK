from rest_framework import serializers

from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):

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


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Публичный профиль: общая информация.
    Без фамилии и без истории платежей.
    """

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
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Детальный профиль (для владельца): с историей платежей.
    """
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
            "payments",  # история платежей только в приватном профиле
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.
    Пароль — write_only, создаём пользователя через create_user.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "username",
            "phone",
            "city",
            "avatar",
            "first_name",
            "last_name",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            **validated_data,
        )
        return user