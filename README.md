# edusite (DRF: ViewSet + Generic)

## Установка
```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Эндпоинты
/api/ — корень DRF


/api/courses/ — CRUD курсов (ViewSet)

/api/lessons/ — список/создание уроков (Generic)

/api/lessons/<id>/ — детальный/редактирование/удаление урока (Generic)

/api/users/ — CRUD пользователей (доп.задание)

/admin/ — админка