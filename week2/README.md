Через Docker Compose можно поднять базу, API платежей и API страховки:

```bash
docker compose up -d db payment-api protection-api
```

База будет доступна на порту `7432`, API платежей (`payment`) на `9001`, API страховки (`protection`) на `9002`.

Накатить миграции:

```bash
cd afisha
uv run alembic upgrade head
```

Запустить приложение:

```bash
uv run uvicorn src.main:app
```

Запустить планировщик:

```bash
uv run taskiq scheduler src.infrastracture.tasks.app:scheduler src.infrastracture.tasks.tasks --log-level INFO
```

Запустить синхронный воркер:

```bash
uv run taskiq worker src.infrastracture.tasks.app:broker_sync src.infrastracture.tasks.tasks
```

Запустить асинхронный воркер:

```bash
uv run taskiq worker src.infrastracture.tasks.app:broker_async src.infrastracture.tasks.tasks
```
