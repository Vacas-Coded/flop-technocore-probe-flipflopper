# GET-only Docs Probe Checklist

1. Confirm route returns HTTP 200 consistently.
2. Run first-contact runner and save artifacts.
3. Run app/inference adapter and save artifacts.
4. Capture auth requirements, schema hints, model names, quota language, and endpoint names.
5. Restrict follow-up probing to safe GET requests only.
6. Do not send POST/PUT/PATCH/DELETE requests in this phase.
7. Prefer OpenAPI, docs, config, and static help pages.
8. Record any base URLs, versions, or rate-limit headers.
9. Preserve raw responses and timestamps.
10. Update evidence template immediately.
