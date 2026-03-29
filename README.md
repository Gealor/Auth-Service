# Инструкция по развертыванию

## 1. Создание .env файла
Создайте в /src/ файл .env и скопируйте параметры из .env.template в новый файл. Если вы хотите задать свои данные для логина, пароля и имени базы данных, тогда поменяйте соответствующие поля POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

## 2. Генерация приватного и публичного ключей
Вводить команды в корневой папке проекта, не в src.
Приватный ключ:

```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out src/core/auth/certs/jwt-private.pem 2048
```

Публичный ключ:

```shell
# Extract the public key from the key pair, which can be used in a certificate
openssl rsa -in src/core/auth/certs/jwt-private.pem -outform PEM -pubout -out src/core/auth/certs/jwt-public.pem
```

## 3. Поднятие docker-compose
В корневой папке проекта (где лежит docker-compose.yml) пропишите
```
docker compose build --no-cache
docker compose up
```

## 4. Применить alembic миграции
После поднятия контейнеров, пропишите в консоли, чтобы применить миграции
```
docker compose exec app sh -c "cd src && uv run alembic upgrade head" 
```

Чтобы откатить миграции пропишите
```
docker compose exec app sh -c "cd src && uv run alembic downgrade base" 
```

# Архитектура

## Схема базы данных

В проекте используется реляционная база данных PostgreSQL. Основные таблицы:

- `users` — пользователи системы:
  - `id` (PK)
  - `first_name`, `last_name`, `patronymic`
  - `email`, `password` (хэш пароля)
  - `is_active` (статус активности)
  - `role_id` (FK -> `roles.id`)
  - `banned_at`, `deleted_at` (soft delete / блокировка)

- `roles` — роли пользователей:
  - `id` (PK)
  - `name` (уникальное наименование)

- `business_elements` — ресурсы/сущности бизнес-области (например, "user", "reports", "settings"):
  - `id` (PK)
  - `name` (уникальное наименование)

- `access_roles_rules` — правила доступа для пар (роль + сущность):
  - `id` (PK)
  - `role_id` (FK -> `roles.id`)
  - `element_id` (FK -> `business_elements.id`)
  - `read_permission` (доступ на чтение собственной сущности)
  - `read_all_permission` (доступ на чтение всех сущностей)
  - `create_permission` (создание)
  - `update_permission` (обновление собственной сущности)
  - `update_all_permission` (обновление любой сущности)
  - `delete_permission` (удаление собственной сущности)
  - `delete_all_permission` (удаление любой сущности)

  Уникальное ограничение `uq_role_element` гарантирует, что на одну роль + ресурс записано ровно одно правило.

- `refresh_tokens` — хранение refresh-токенов JWT, данная таблица сделана для хранения актуальных refresh токенов, т.к. они являются долгоживущими. Я посчитал, что функционал /logout должен работать по следующему принципу: пользователь дергает этот эндпоинт и его refresh токен затирается и на фронтенд отправялется сообщение, что надо удалить access-токен из заголовков, либо кук (cookie)
  - `user_id` (PK для привязки к пользователю)
  - `token` (строка)

## Архитектура прав доступа (RBAC)

1. Пользователь (`users`) связан с ролевой записью (`roles`).
2. Для каждой роли задаются правила (`access_roles_rules`) через ресурс (`business_elements`).
3. Проверка прав выполняется по элементу и действию:
   - `read` / `read_all`
   - `create`
   - `update` / `update_all`
   - `delete` / `delete_all`
4. В бизнес-логике (сервис/роуты) при обращении к API сначала проверяется роль пользователя и правило для текущего ресурса.

## Пример сценария

- Роль `superadmin`:
  - `business_elements` = `users`, `roles`, `permissions`
  - все флаги `*_all_permission` = true для полного доступа

- Роль `user`:
  - `business_elements` = `users`
  - `read_permission` / `update_permission` могут быть true для работы со своим профилем
  - `read_all_permission`, `update_all_permission`, `delete_all_permission` = false
