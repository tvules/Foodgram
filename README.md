<h1 align="center">Foodgram</h1>

**[Foodgram](http://51.250.10.46)** — Онлайн-сервис «Продуктовый помощник».
Здесь Вы можете публиковать рецепты, подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов,
необходимых для приготовления одного или нескольких выбранных блюд.

---

### Технологии

- Django
- Django REST framework
- PostgreSQL
- Nginx
- Docker

### Инструкции по установке

#### 1. Клонируйте репозиторий

```
git@github.com:tvules/foodgram-project-react.git
```

#### 2. Создайте `.env` файл в директории `infra/`:

```
SECRET_KEY="^(@034)g%3&48!dgl38$erhjo73anqqhh*sku_do2k=s!fsm*w"

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

*значения приведены для примера

#### 3. Выполните команду для сборки контейнера:


```
docker compose up
```

Если у Вас не установлен Docker, 
установите его используя эти [инструкции](https://docs.docker.com/engine/install/).

#### 4. Создайте супер пользователя:

```
docker compose exec infra_web_1 python manage.py createsuperuser
```

---

<h5 align="center">Автор проекта: <a href="https://github.com/tvules">Petrukhin Ilya</a></h5>
