Учебный проект по Django REST Framework (DRF)  
Домашнее задание: **ViewSet и Generic классы**.

---

## 📘 Описание проекта

Проект реализует базовый REST API для управления курсами и уроками, а также включает кастомную модель пользователя с авторизацией по email.

### Функционал:
- Кастомная модель `User` с полями: `email`, `phone`, `city`, `avatar`.
- Модель `Course` (название, описание, превью).
- Модель `Lesson` (название, описание, превью, видео, связь с курсом).
- Полный CRUD для:
  - **Course** — через ViewSet.
  - **Lesson** — через GenericAPIView.
- Эндпоинты для управления пользователями (доп.задание).
- Медиафайлы и загрузка изображений.
- Проверено через **Postman**.

---

## ⚙️ Установка и запуск

### 1️⃣ Клонировать проект
```bash
git clone https://github.com/AHMEDaaddd/StudiiiiWEBBACK.git
cd StudiiiiWEBBACK

2️⃣ Создать виртуальное окружение и активировать
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1

3️⃣ Установить зависимости
pip install -r requirements.txt


(или просто вручную установить Django и DRF, если файла requirements.txt нет):

pip install django djangorestframework pillow

4️⃣ Применить миграции
python manage.py makemigrations
python manage.py migrate

5️⃣ Создать суперпользователя
python manage.py createsuperuser

6️⃣ Запустить сервер
python manage.py runserver
