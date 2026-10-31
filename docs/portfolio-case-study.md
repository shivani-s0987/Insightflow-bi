# Portfolio case study: InsightFlow BI

## Business problem

Teams often receive CSV/Excel exports but must switch between spreadsheets, ad hoc scripts, and presentation tools to validate data and communicate results. InsightFlow BI explores a single workflow from ingestion and quality checks to repeatable preparation, aggregation, visualization, and export.

## Technical choices

- **Django REST Framework** provides a conventional, testable API and built-in secure password hashing/session/CSRF foundations.
- **Workspace memberships** keep tenant authorization explicit and server-side rather than relying on route hiding in the browser.
- **Pandas** makes the initial analytical operations concise and testable while upload limits keep the in-memory approach bounded.
- **JSON transformation steps** preserve an inspectable sequence of allowed operations instead of executing arbitrary expressions.
- **React + TypeScript + Recharts** separate the dashboard UI from backend query calculations.
- **PostgreSQL with local SQLite fallback** supports a smooth local setup and a realistic deployment path.

## Engineering challenges addressed

1. Validate file size/type and keep uploaded originals private.
2. Avoid frontend-trusted authorization by checking workspace membership in each resource endpoint.
3. Use explicit operation and aggregation allowlists to avoid arbitrary code execution and unsafe SQL construction.
4. Make the dashboard query real persisted dataset rows rather than client-side fixture KPIs.
5. Neutralize formula-leading text during CSV export.
6. Keep the local development path accessible without requiring a database server.

## Evidence and measurements

Do not fill this section with invented benchmarks. After running tests in your environment, record:

- Backend test count and pass/fail result.
- Frontend test count and production build result.
- Upload/profile/aggregation timings for a published, reproducible synthetic fixture (include file size, row/column count, hardware, and environment).
- Results of a cross-workspace authorization regression test.
- Screenshots of actual in-product output.

## Current scope and next improvements

The current implementation is a runnable MVP, not a production-certified SaaS. Priority improvements: asynchronous Celery ingestion and report jobs, private object storage, worksheet selection, versioned materialized analytical data, richer dashboard layout editing, PDF report design, password reset/email verification, invitation/role administration, complete audit event emission, OpenAPI schema generation, and Playwright critical-journey tests.
