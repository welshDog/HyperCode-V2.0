# NemoClaw (NVIDIA) — HyperCode V2.0 Integration Readiness

This document prepares HyperCode V2.0 to use NemoClaw + OpenClaw sandboxed agents with NVIDIA cloud inference (Nemotron).

## What NemoClaw Is (Operationally)

NemoClaw is a CLI-first workflow that provisions an OpenShell sandbox running OpenClaw with:

- strict filesystem + network policy controls
- inference routed through an OpenShell gateway
- NVIDIA cloud inference via build.nvidia.com models (Nemotron)

Reference quickstart: https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html

## Prerequisites

NemoClaw quickstart prerequisites:

- Ubuntu 22.04+ (recommended via WSL2 on Windows)
- Node.js 20+ and npm 10+ (installer recommends Node.js 22)
- Docker installed and running
- NVIDIA OpenShell installed

Windows note:

- Use WSL2 Ubuntu 22.04+ for the installer and CLI workflow.
- Docker Desktop must be running with WSL integration enabled for the Ubuntu distro you use.

## Environment Variables

NemoClaw inference switching requires `NVIDIA_API_KEY`:

- Get a key from build.nvidia.com
- Set it in your shell before onboarding or switching inference providers

Reference: https://docs.nvidia.com/nemoclaw/latest/inference/switch-inference-providers.html

For repo hygiene, keep secrets outside git. Use `.env.nemoclaw.example` as a template and export values in your shell before running NemoClaw.

## Installation (CLI-First)

Run the official installer which also onboards a sandbox:

```bash
curl -fsSL https://nvidia.com/nemoclaw.sh | bash
```

When complete, you will see commands similar to:

```bash
nemoclaw <sandbox-name> connect
nemoclaw <sandbox-name> status
nemoclaw <sandbox-name> logs --follow
```

## Sanity Check

1) Connect to the sandbox:

```bash
nemoclaw <sandbox-name> connect
```

2) In the sandbox shell, run the OpenClaw CLI once:

```bash
openclaw agent --agent main --local -m "hello" --session-id test
```

## Local Inference (Optional)

NemoClaw supports switching inference providers at runtime. For local deployment experiments, this repo includes an optional compose file you can enable as a separate profile:

- [docker-compose.nim.yml](file:///h:/HyperStation%20zone/HyperCode/HyperCode-V2.0/docker-compose.nim.yml)

This is intentionally isolated from the default stack so it cannot break the core system.

## HyperCode Integration Map

HyperCode can treat NemoClaw as an external “inference + tool sandbox” layer. Recommended integration path:

1) Keep HyperCode core services unchanged (Core API / Celery / Orchestrator).
2) Use NemoClaw sandbox for:
   - safe code execution tasks
   - gated network access (approved domains)
   - high-quality inference calls via NVIDIA models
3) Add a single “bridge” component later (optional):
   - a small service that submits prompts to the sandbox and returns results to HyperCode.

## Guardrails

- Do not commit `NVIDIA_API_KEY` to the repo.
- Prefer allowlist policy updates (approved domains) rather than global network access.
- Keep `/api/health` and Prometheus `/metrics` checks separate from NemoClaw, so core operations remain observable even if NemoClaw is down.
