# Food Recipes App



### Описание

Веб-приложение для публикации кулинарных рецептов. Пользователи могут добавлять рецепты, просматривать чужие публикации, подписываться на любимых авторов и формировать список покупок для приготовления блюд.

### Функциональность

- Регистрация и аутентификация пользователей

- Публикация рецептов с изображениями и ингредиентами

- Подписка на других пользователей

- Добавление рецептов в "Избранное"

- Формирование списка покупок

- Фильтрация рецептов по тегам

### Технологии

**Backend:** Python, Django, Django REST Framework, Djoser

**Frontend:** React (или шаблоны Django, если не используется React)

**База данных:** PostgreSQL

**Контейнеризация:** Docker, Docker Compose

**Автоматическое развертывание:** GitHub Actions

### Установка и запуск

**1. Клонирование репозитория**

```bash
git clone https://github.com/mbur17/foodgram.git
cd foodgram
```

**2. Запуск с Docker**

Создайте .env файл и добавьте переменные окружения:

```bash
# db
POSTGRES_DB=postgres
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
DB_NAME=project_db
# django
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-server-ip,your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,http://your-server-ip
```

**Соберите и запустите контейнеры:**

```bash
docker-compose up -d --build
```

**Выполните миграции, создайте суперпользователя, соберите статику и загрузите ингредиенты,
предварительно переместив ingredients.json из data/ в app/ контейнера backend:**

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend cp -r /app/collected_static/. /backend_static/static/
docker-compose exec backend python manage.py python manage.py load_data
```

**3. Доступ к приложению**

API-документация доступна по адресу: http://localhost/api/docs/

Веб-интерфейс: http://localhost/

### Разработка

**Локальный запуск без Docker**

```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Автор:
[Буряковский Максим](https://github.com/mbur17)

## Лицензия

Этот проект распространяется под лицензией MIT.

