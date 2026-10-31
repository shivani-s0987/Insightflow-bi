# API guide

Base URL: `/api/v1/`. JSON errors use DRF validation responses with a safe `detail` or stable `code` where implemented. Auth is a Django session cookie; unsafe methods require CSRF.

## Registration example

```http
POST /api/v1/auth/register/
Content-Type: application/json

{"name":"Ada Analyst","email":"ada@example.com","password":"a-long-unique-password"}
```

Registration creates a user and an owner membership in a new workspace. It does not verify the email address; configure a verified email flow before public deployment.

## Upload example

`POST /api/v1/datasets/upload/` uses `multipart/form-data` fields `workspace` and `file`, with optional `name`. Supported formats: CSV and XLSX. The response includes dataset ID, row/column counts and inferred schema.

## Analytics example

```json
{
  "dataset_id": 1,
  "group_by": "region",
  "metric": "revenue",
  "aggregation": "sum",
  "filters": [{"column":"status","op":"eq","value":"completed"}],
  "limit": 50
}
```

Allowed aggregations: `count`, `distinct_count`, `sum`, `mean`, `min`, `max`, `median`. Filter operations are `eq`, `ne`, `contains`, `gt`, `gte`, `lt`, `lte`. Metric types are validated. Query results are capped at 500 groups. The current engine uses Pandas on bounded files rather than arbitrary SQL generation.

## Auth/permissions

Call `GET /api/v1/auth/csrf/` before login/registration when using a browser client; Django sets the CSRF cookie. Include credentials and `X-CSRFToken` for write calls. `GET /auth/me/` returns memberships. A missing membership returns 404 for workspace-owned resource reads to avoid disclosing resource existence. Viewers can read; write endpoints require owner/administrator/analyst.

OpenAPI generation is not currently configured. DRF's browsable API is enabled only in development.
