from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription


class LessonAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            username="owner",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            username="other",
        )
        self.moderator = User.objects.create_user(
            email="moderator@example.com",
            password="testpass123",
            username="moderator",
        )
        # модератором считаем staff-пользователя
        self.moderator.is_staff = True
        self.moderator.save()

        self.course = Course.objects.create(
            title="Test course",
            description="test description",
            owner=self.owner,
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Lesson 1",
            description="description",
            owner=self.owner,
        )
        # урок другого пользователя для проверки фильтрации списка
        self.foreign_lesson = Lesson.objects.create(
            course=self.course,
            title="Foreign lesson",
            description="description",
            owner=self.other_user,
        )

        self.lessons_list_url = reverse("lesson-list-create")
        self.lesson_detail_url = reverse("lesson-detail", kwargs={"pk": self.lesson.pk})
        self.subscription_url = reverse(
            "course-subscription",
            kwargs={"course_id": self.course.pk},
        )

    # ---------- LIST ----------

    def test_lessons_list_requires_authentication(self):
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_only_own_lessons_in_list(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # пагинация PageNumberPagination -> данные в поле "results"
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.lesson.id)

    def test_moderator_sees_all_lessons_in_list(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], Lesson.objects.count())

    # ---------- CREATE ----------

    def test_owner_can_create_lesson(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "course": self.course.id,
            "title": "New lesson",
            "description": "Text",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        response = self.client.post(self.lessons_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Lesson.objects.filter(owner=self.owner, title="New lesson").count(),
            1,
        )

    def test_moderator_cannot_create_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        data = {
            "course": self.course.id,
            "title": "Lesson from moderator",
            "description": "Text",
        }
        response = self.client.post(self.lessons_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- RETRIEVE ----------

    def test_owner_can_retrieve_lesson(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lesson.id)

    def test_other_user_cannot_retrieve_foreign_lesson(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_retrieve_any_lesson(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ---------- UPDATE / DELETE ----------

    def test_owner_can_update_lesson(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            self.lesson_detail_url,
            {"title": "Updated title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated title")

    def test_other_user_cannot_update_foreign_lesson(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            self.lesson_detail_url,
            {"title": "Hacked title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_lesson(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    # ---------- SUBSCRIPTION ----------

    def test_anonymous_cannot_toggle_subscription(self):
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_subscribe_and_unsubscribe(self):
        self.client.force_authenticate(user=self.owner)

        # 1-й вызов -> создаёт подписку
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.owner, course=self.course).exists(),
        )

        # 2-й вызов -> удаляет подписку
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.owner, course=self.course).exists(),
        )

    def test_is_subscribed_flag_in_course_detail(self):
        self.client.force_authenticate(user=self.owner)

        # без подписки
        course_detail_url = reverse("course-detail", kwargs={"pk": self.course.pk})
        response = self.client.get(course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

        # с подпиской
        Subscription.objects.create(user=self.owner, course=self.course)
        response = self.client.get(course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])