# Testing strategy

## Backend

Run `cd backend && python manage.py test`. Included tests cover transformation correctness, invalid column rejection, real CSV upload/profile behavior, and cross-workspace dataset access denial. Expand with role-matrix tests for every endpoint, XLSX malformed/oversized upload cases, KPI math edge cases, formula injection, export authorization, and retry/idempotency scenarios.

## Frontend

Run `cd frontend && npm test` and `npm run build`. The current Vitest tests verify public landing page value proposition and workflow rendering. The API integration uses Django session/CSRF cookies; full authenticated browser-flow tests with Playwright are not yet implemented.

## Manual smoke test

1. Start backend and frontend using README steps.
2. Run `python manage.py seed_demo` and sign in with the local-only demo credentials.
3. Confirm overview charts query real seed rows.
4. Open Datasets → inspect a dataset profile → preview records.
5. Upload a small CSV; apply a preparation step; preview and save the pipeline.
6. Use Analytics Explorer to group/aggregate a field; save the view as a dashboard.
7. Save a report and download CSV/XLSX.
8. Create a second user and verify they cannot access the first user's workspace IDs.

Never interpret a successful build as evidence of a complete end-to-end journey. Record exact environment and outcomes when reporting results.
