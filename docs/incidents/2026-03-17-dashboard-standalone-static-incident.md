# Incident Report: Dashboard “Crash” During Play Test (Standalone Static Assets)

## Summary

During an end-to-end play test of HyperStation Mission Control (local standalone build), the UI loaded but key interactions (sign-in, tab switching, executing commands) appeared non-responsive. The root cause was missing Next.js standalone runtime assets (`_next/static`), causing client-side hydration to fail.

This was a packaging/startup issue, not a code regression in the React components.

## Impact

- **User-visible:** Page renders HTML, but interactive controls do not function reliably.
- **Scope:** Local/CI runs that start `server.js` without ensuring the standalone bundle includes `.next/static` (and `public/` if used).
- **Severity:** High (breaks core user journeys), but contained to deployment/startup workflow.

## Timeline (Reconstructed)

1) Dashboard started from the generated standalone server entrypoint.
2) Browser loaded `/` successfully (HTML returned).
3) Browser requested one or more `/_next/static/chunks/*.js` assets.
4) Requests returned **404 Not Found** (standalone package missing `.next/static`).
5) Client-side hydration did not complete, so UI interactions appeared “crashed”.
6) Resolution was to prepare/copy the required static assets into the standalone runtime folder and restart the server.

## Root Cause

Next.js `output: "standalone"` produces a runnable `server.js` bundle but requires runtime assets to be present alongside it:

- `.next/static/**` (chunks, runtime, css)
- `public/**` (if any)

If these assets are not present in the standalone folder, the server will still return HTML but will not be able to serve the referenced chunk files, producing 404s and breaking hydration.

## Contributing Factors

- Startup command did not enforce a “standalone preparation” step.
- No guardrail test existed that asserts `_next/static` is servable after `next build`.
- No explicit operational runbook described the correct standalone packaging steps.

## Detection

Primary signals:

- Browser network trace shows `/_next/static/chunks/*.js` returning 404.
- UI appears rendered but non-interactive (no client hydration).

Secondary signals:

- Accessibility scan and UI automation can hang or falsely “pass” partial checks if hydration never runs.

## Resolution

Implemented an automated standalone preparation and verification path:

- `agents/dashboard/scripts/prepare-standalone.mjs` copies `.next/static` and `public` into the standalone runtime folder.
- `agents/dashboard/scripts/start-standalone.mjs` runs the prepare step and then starts `server.js` from the correct runtime directory.
- `agents/dashboard/scripts/verify-standalone.mjs` deletes the standalone static folder, prepares it again, starts a server on a random port, and asserts an HTML-referenced chunk returns 200.

CI gate was updated to use the new start flow and to run the verification step before running axe scans.

## Preventive Measures

### Enhanced Error Handling (Startup)

- Fail-fast if standalone output is missing or incomplete.
- Ensure `.next/static` is always present before server start.

### Input Validation (Operational)

- Scripts validate required paths and provide actionable error messages (“Run `npm run build` first”).

### Resource Monitoring / Early Warning Alerts

- Added a Prometheus alert rule to page critical when the dashboard container is missing:
  - `DashboardContainerMissing` in `monitoring/prometheus/docker_alerts.yml`

### Automated Recovery

- Standalone preparation automatically restores missing static assets on every start (idempotent copy).

## Rollback Procedure

If the dashboard fails to start or serve `_next/static`:

1) Revert to the last known-good `main` commit.
2) Run `npm -C agents/dashboard run build`.
3) Start with `npm -C agents/dashboard run start:standalone`.

If CI is blocked due to this gate:

- Temporarily disable only the standalone verification step in the accessibility workflow, not the axe scans, and re-enable after fixing build packaging.

## Verification / Tests Added

- `npm -C agents/dashboard run verify:standalone`:
  - simulates missing standalone static assets,
  - prepares the runtime,
  - verifies a real chunk referenced by HTML is servable (200),
  - terminates the server cleanly.

## Success Metrics

- 0 occurrences of `_next/static` 404s in CI and local standalone runs.
- “Time to usable UI” stays stable (no hydration failure).
- Accessibility gate remains deterministic (axe scans run on fully-hydrated UI).

