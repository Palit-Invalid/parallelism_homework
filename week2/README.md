# Запуск проекта в production режиме

```bash
cp .env example.env
docker compose up
```

# Запуск проекта для разработки

Особенности:

- автоматический перезапуск API при изменении исходников;
- проброс файлов миграции внутрь контейнера.

Запуск:

```bash
docker compose --env-file dev.env up
```
