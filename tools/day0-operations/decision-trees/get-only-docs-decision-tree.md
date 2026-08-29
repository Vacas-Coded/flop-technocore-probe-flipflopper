# GET-only Docs Probe Decision Tree

- Is the route HTTP 200?
  - No -> stop, keep watcher active.
  - Yes -> run first-contact runner.
- Does the surface classify as `api_like`, `app`, or `inference`?
  - No -> stop, treat as other surface.
  - Yes -> run app/inference adapter.
- Are docs/config/openapi/static GET endpoints visible?
  - No -> stop after evidence capture.
  - Yes -> continue with GET-only collection.
- Would the next request require POST or credentials not clearly meant for automation?
  - Yes -> stop and ask before proceeding.
  - No -> continue with safe GET-only probing.
