# credits-service

Сервис кредитов и AI-генераций. Задание — в [TASK.md](TASK.md).

## Запуск

Через Docker:

```bash
docker compose up --build
```

Поднимутся MySQL, Redis и RabbitMQ, применятся миграции, запустятся два процесса:

- `api` — HTTP API на http://localhost:8000, Swagger на http://localhost:8000/docs;
- `worker` — обработчик очереди `generations`.

Панель RabbitMQ: http://localhost:15672, логин и пароль `guest` / `guest`.

Локально, инфраструктура в Docker:

```bash
docker compose up -d mysql redis rabbitmq
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn apps.api.main:app --reload
uv run python -m apps.worker.main
```

Проверки:

```bash
uv run pytest
uv run ruff check .
uv run mypy
```

## Контракт API

| Метод и путь | Тело запроса | Ответы |
|---|---|---|
| `GET /health` | — | `200 {"status": "ok"}` |
| `POST /webhooks/purchase` | `event_id`, `user_id`, `product_id`, `credits`, заголовок `X-Webhook-Secret` | `200 {"status": "processed"}` или `200 {"status": "duplicate"}`; `401` при неверном секрете |
| `POST /generations` | `user_id`, `prompt` | `202 {"id", "status"}`; `402` при нехватке кредитов |
| `GET /generations/{id}` | — | `200 {"id", "user_id", "status", "cost", "result_url", "error", "created_at", "updated_at"}`; `404` |
| `GET /users/{user_id}/balance` | — | `200 {"user_id", "balance"}` |
| `GET /users/{user_id}/transactions?limit=50` | — | `200 {"items": [{"amount", "kind", "reference_id", "created_at"}]}`, `limit` от 1 до 200 |

Статусы генерации: `pending`, `processing`, `completed`, `failed`. Виды операций: `purchase`, `generation_debit`, `generation_refund`. Неверное тело запроса — `422`.

## Пример

```bash
curl -X POST localhost:8000/webhooks/purchase \
  -H 'Content-Type: application/json' -H 'X-Webhook-Secret: change-me' \
  -d '{"event_id": "evt-1", "user_id": "u1", "product_id": "credits_50", "credits": 50}'

curl -X POST localhost:8000/generations \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "u1", "prompt": "a cat in space"}'

curl localhost:8000/generations/<id>
curl localhost:8000/users/u1/balance
curl localhost:8000/users/u1/transactions
```

Стоимость генерации задаётся `GENERATION_COST`, по умолчанию 10.

## Архитектура

Зависимости направлены внутрь, к `domain`:

```
apps  →  interface  →  application  →  domain  ←  infrastructure
                                                    core
```

| Папка | Что там |
|---|---|
| `apps/` | Точки входа процессов `api` и `worker` |
| `components/interface/` | FastAPI-роутеры, схемы, зависимости, подписчик воркера, сборка контейнера (`composition/`) |
| `components/application/` | Use case'ы. Без SQLAlchemy, FastAPI, Redis и FastStream |
| `components/domain/` | Сущности, `types/enums`, ошибки, протоколы репозиториев и внешних сервисов. Без зависимостей от фреймворков |
| `components/infrastructure/` | Реализации протоколов: `stores/mysql`, `stores/redis`, `workers/rabbit`, `clients` |
| `components/core/` | Настройки и логирование |

Соглашения:

- Одна транзакция — один `async with uow`. Всё, что не закоммичено через `uow.commit()`, откатывается при выходе из блока.
- Use case'ы зависят только от протоколов из `domain/protocols`. Реализации подставляются в `interface/api/dependencies.py` и `interface/worker/app_factory.py`.
- Один основной класс на файл, строковые константы — enum'ы в `domain/types/enums`.
- Схема БД меняется только новыми ревизиями Alembic.
