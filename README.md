# api_migration

## Technical description of the Migration project

### Simple start

```sh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Custom Roles

Anonymous - can register.

Authenticated user (user) - can create, view and delete objects.

### User registration algorithm
1. The user sends a POST request with the username and password parameters to / api / v1 / auth /.
2. The user sends a POST request with the parameters username and password to / api / v1 / token /, in response to the request he receives a JWT token ('access').

These operations are performed once, during user registration. As a result, the user receives a token and can work with the API, sending this token with each request (it is important to remember that the header should look like this - Authorization: Bearer <access>).


### API Resources

AUTH resource: registration.

TOKEN resource: authorization.

CREDENTIALS.

MIGRATION TARGETS.

MIGRATIONS.

MOUNT POINTS.

WORK LOADS.

Each resource is described in the / swagger / documentation: endpoints, allowed types of requests, access rights and additional parameters, if necessary, are indicated.

## Техническое описание проекта Migration

### Пользовательские роли

Аноним — может зарегистрироваться.

Аутентифицированный пользователь (user) — может создавать, просматривать и удалять объекты.

### Алгоритм регистрации пользователей
1. Пользователь отправляет POST-запрос с параметрами username и password на /api/v1/auth/.
2. Пользователь отправляет POST-запрос с параметрами username и password на /api/v1/token/, в ответе на запрос ему приходит JWT-токен ('access').

Эти операции выполняются один раз, при регистрации пользователя. В результате пользователь получает токен и может работать с API, отправляя этот токен с каждым запросом (важно помнить что header должен выглядеть так - Authorization: Bearer <access>).


### Ресурсы API

Ресурс AUTH: регистрация.

Ресурс TOKEN: авторизация.

Ресурс CREDENTIALS: учетные данные.

Ресурс MIGRATION TARGETS: итоги миграции.

Ресурс MIGRATIONS: миграции.

Ресурс MOUNT POINTS: точки монтирования.

Ресурс WORK LOADS: источники миграции.

Каждый ресурс описан в документации /swagger/: указаны эндпойнты, разрешённые типы запросов, права доступа и дополнительные параметры, если это необходимо.

