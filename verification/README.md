# HyperCode Verification Suite

This directory contains the verification tools for HyperCode V2.0.

## Contents
- `VERIFICATION_PROTOCOL.md`: The strategy document.
- `run.py`: The main entry point for running the verification.
- `test_system.py`: The pytest suite covering infrastructure, API, and agents.
- `health_check.py`: (Optional) A simple script for quick health checks.

## Usage
To run the full verification suite and generate a report:

```bash
python verification/run.py
```

This will output `VERIFICATION_REPORT.md` in the root directory.

## Troubleshooting
- **Docker CLI Errors**: If you see `Docker CLI failed`, it might be due to Docker Desktop issues on Windows. The suite will skip these checks and focus on HTTP connectivity.
- **Timeouts**: If Core API tests fail with timeouts, ensure `hypercode-core` is running and healthy. You can check logs with `docker logs hypercode-core`.
