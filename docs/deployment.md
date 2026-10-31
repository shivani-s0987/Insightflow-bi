# Deployment and operations

## Runtime

Docker Compose includes PostgreSQL 16, a Django/Gunicorn backend, and an Nginx-served Vite build. Persistent volumes store PostgreSQL data and private uploads. The backend container runs migrations and collects static files at startup; for larger production deployments, move migrations into a controlled release step and run multiple app instances behind a TLS reverse proxy.

## Environment

Required production settings: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `MAX_UPLOAD_BYTES`, and private `MEDIA_ROOT`. Configure `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` for Compose. `VITE_API_URL` is compiled into the frontend at build time and must point to the public API origin.

## Backup and restore

Back up PostgreSQL and the private upload volume together; they jointly represent metadata and source files. Example database backup:

```bash
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > insightflow.sql
```

Restore into a separately verified database (do not overwrite production blindly):

```bash
cat insightflow.sql | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Back up the `private_uploads` volume using your container/volume backup tooling. Test restoring database and files in a clean environment and verify that sample dataset profiles and exports still work. Define retention, encryption, access, and recovery-point objectives according to the deployment's data sensitivity.

## Health and monitoring

`GET /health/` checks that the Django process responds; it does not yet test database connectivity. Add DB/cache/storage readiness probes, structured logs with correlation IDs, queue monitoring, and alerts before production. Docker Compose is a convenient deployment baseline, not a substitute for a reviewed production infrastructure plan.
