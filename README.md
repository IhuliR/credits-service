# Credits Service

Асинхронный сервис учёта кредитов и запуска AI-генераций. Он принимает webhook об оплате, ведёт баланс и историю операций, создаёт задачи генерации и обрабатывает их через RabbitMQ с таймаутами, повторными попытками и возвратом средств при окончательной ошибке.

## Возможности

- идемпотентное начисление кредитов по `event_id` покупки;
- конкурентно-безопасное списание баланса в MySQL;
- кэширование чтения баланса в Redis;
- асинхронная обработка генераций через RabbitMQ и FastStream;
- retry с экспоненциальной задержкой для временных ошибок провайдера;
- атомарный перевод генерации в `failed` и возврат кредитов;
- миграции Alembic и unit-тесты ключевой бизнес-логики.

## Стек

Python 3.12, FastAPI, SQLAlchemy 2, MySQL 8.4, Redis, RabbitMQ, FastStream, Alembic, Pydantic Settings, pytest, Ruff, mypy и uv.

## Архитектура

```mermaid
flowchart LR
    Client[API client] --> API[FastAPI API]
    Payments[Payment system] --> API
    API --> MySQL[(MySQL)]
    API <--> Redis[(Redis balance cache)]
    API --> RabbitMQ[(RabbitMQ)]
    RabbitMQ --> Worker[FastStream worker]
    Worker --> Provider[Generation provider]
    Worker --> MySQL
    Worker --> Redis
    Alembic[Alembic] --> MySQL
```

Зависимости кода направлены к доменному слою:

```text
apps → interface → application → domain
       interface → infrastructure → domain
apps / interface / infrastructure → core
```

| Каталог | Назначение |
|---|---|
| `apps/` | Точки входа API и worker |
| `components/interface/` | HTTP-роутеры, схемы, зависимости, worker handler и composition root |
| `components/application/` | Сценарии приложения, работающие через доменные протоколы |
| `components/domain/` | Сущности, перечисления, ошибки и протоколы |
| `components/infrastructure/` | MySQL-репозитории, Redis-кэш, RabbitMQ publisher и fake-provider |
| `components/core/` | Настройки и логирование |
| `migrations/` | Миграции Alembic |

Подробности о транзакциях, блокировках и компромиссах описаны в [инженерных решениях](docs/engineering-decisions.md).

## Быстрый запуск

Нужны Docker и Docker Compose.

```bash
docker compose up --build
```

После запуска доступны:

- API: <http://localhost:8000>;
- Swagger UI: <http://localhost:8000/docs>;
- RabbitMQ Management: <http://localhost:15672>, `guest` / `guest` — только для локального окружения.

Compose поднимает MySQL, Redis и RabbitMQ, применяет миграции, затем запускает API и worker. Проверка состояния API:

```bash
curl http://localhost:8000/health
```

Остановка сервисов:

```bash
docker compose down
```

## Локальная разработка

Установите [uv](https://docs.astral.sh/uv/) и запустите инфраструктуру:

```bash
docker compose up -d mysql redis rabbitmq
cp .env.example .env
uv sync --locked
uv run alembic upgrade head
```

API и worker запускаются в отдельных терминалах:

```bash
uv run uvicorn apps.api.main:app --reload
```

```bash
uv run python -m apps.worker.main
```

Отдельно создавать пользователя не требуется. Запрос баланса неизвестного `user_id` возвращает `0`, а первая успешная покупка создаёт запись его баланса.

## Настройки

Настройки читаются из переменных окружения и файла `.env`. Шаблон находится в `.env.example`.

| Переменная | Значение по умолчанию | Назначение |
|---|---:|---|
| `MYSQL_DSN` | `mysql+aiomysql://credits:credits@localhost:3306/credits` | Подключение к MySQL |
| `REDIS_URL` | `redis://localhost:6379/0` | Подключение к Redis |
| `RABBIT_URL` | `amqp://guest:guest@localhost:5672/` | Подключение к RabbitMQ |
| `WEBHOOK_SECRET` | `change-me` | Секрет заголовка purchase webhook |
| `GENERATION_COST` | `10` | Стоимость одной генерации |
| `BALANCE_CACHE_TTL_SECONDS` | `300` | TTL кэша баланса |
| `GENERATIONS_QUEUE` | `generations` | Имя очереди задач |
| `PROVIDER_MAX_ATTEMPTS` | `3` | Максимальное число вызовов провайдера |
| `PROVIDER_TIMEOUT_SECONDS` | `5` | Таймаут одной попытки в секундах |
| `PROVIDER_RETRY_BASE_DELAY_SECONDS` | `1` | Базовая задержка retry в секундах |
| `LOG_LEVEL` | `INFO` | Уровень логирования |

Значения Compose предназначены для демонстрационного локального запуска. Перед использованием в другом окружении замените учётные данные и `WEBHOOK_SECRET`.

## API

| Метод и путь | Назначение | Основные ответы |
|---|---|---|
| `GET /health` | Проверка API | `200` |
| `POST /webhooks/purchase` | Начисление кредитов; нужен `X-Webhook-Secret` | `200 processed/duplicate`, `401` |
| `POST /generations` | Списание кредитов и создание задачи | `202`, `402` при недостаточном балансе |
| `GET /generations/{generation_id}` | Статус и результат генерации | `200`, `404` |
| `GET /users/{user_id}/balance` | Текущий баланс | `200` |
| `GET /users/{user_id}/transactions?limit=50` | История операций, `limit` от 1 до 200 | `200` |

Статусы генерации: `pending`, `processing`, `completed`, `failed`. Типы операций: `purchase`, `generation_debit`, `generation_refund`.

## Демонстрационный сценарий

Начислите кредиты:

```bash
curl -X POST http://localhost:8000/webhooks/purchase \
  -H 'Content-Type: application/json' \
  -H 'X-Webhook-Secret: change-me' \
  -d '{"event_id":"evt-demo-1","user_id":"user-demo","product_id":"credits-50","credits":50}'
```

Повтор того же запроса вернёт `duplicate` и не увеличит баланс второй раз.

Создайте генерацию:

```bash
curl -X POST http://localhost:8000/generations \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"user-demo","prompt":"a lighthouse in a storm"}'
```

Полученный `id` можно использовать для опроса состояния:

```bash
curl http://localhost:8000/generations/<generation_id>
curl http://localhost:8000/users/user-demo/balance
curl http://localhost:8000/users/user-demo/transactions
```

Встроенный fake-provider поддерживает специальные маркеры в `prompt`:

| Маркер | Поведение |
|---|---|
| без маркера | Успех через 0,1–0,5 секунды |
| `[flaky:N]` | Первые `N` вызовов завершаются временной ошибкой |
| `[fail]` | Постоянная ошибка без retry, затем refund |
| `[slow]` | Вызов дольше таймаута; с настройками по умолчанию — три попытки, `failed` и refund примерно за 18 секунд |

Счётчик `[flaky:N]` хранится в памяти процесса worker, поэтому этот режим предназначен только для локальной демонстрации.

## Конкурентность и идемпотентность

- `purchase_events.event_id` защищён `UNIQUE`-ограничением MySQL; повторный webhook возвращает `duplicate`.
- Баланс при создании Generation читается через `SELECT ... FOR UPDATE`; списание, debit и Generation фиксируются одной транзакцией.
- Worker атомарно переводит только `pending → processing` под блокировкой строки и вызывает провайдера уже после освобождения DB-lock.
- Финальный refund выполняет `processing → failed`, увеличение баланса и запись `generation_refund` одной транзакцией под блокировкой Generation.
- Redis инвалидируется только после успешного MySQL commit в сценариях purchase и refund.

## Проверки

```bash
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
docker compose config --quiet
```

Unit-тесты используют in-memory fakes и не требуют запущенных MySQL, Redis или RabbitMQ. Реальное поведение блокировок и полный transport flow проверяются отдельным интеграционным или smoke-запуском Compose.

## Известные ограничения

- Transactional outbox не реализован: сбой после MySQL commit, но до RabbitMQ publish может оставить Generation в `pending`.
- Reconciler для зависших `pending` и `processing` отсутствует.
- Для неожиданных инфраструктурных ошибок нет отдельной управляемой transport retry/requeue policy.
- Между MySQL commit и Redis invalidation остаётся небольшое окно устаревшего кэша; при недоступности Redis значение живёт до TTL.
- Конкурентные гарантии `SELECT ... FOR UPDATE` не подтверждаются unit-тестами с in-memory fakes и требуют теста с реальной MySQL и несколькими сессиями.

Более подробный разбор — в [docs/engineering-decisions.md](docs/engineering-decisions.md).
