# Test Upgrade Audit - 2026-02-13

## 🚨 Critical Finding: Test Suite Execution Failure

**Status**: 🔴 FAILED
**Blocker**: `ImportError` / `ValidationError` during collection.

### Issue Description
The test suite fails to collect tests because of an `ImportError` triggered by Pydantic validation.
When `pytest` starts, it loads `tests/conftest.py`.
`tests/conftest.py` imports `main` at the top level:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app  # <--- IMPACT POINT
```
`main.py` imports `app.routers.agents`, which imports `app.services.agent_registry`, which calls `get_settings()`.
`get_settings()` instantiates `Settings()`, which attempts to validate `HYPERCODE_DB_URL` from environment variables.
Since the `mock_env_vars` fixture in `conftest.py` has **not run yet** (fixtures run at test execution time, not import time), the validation fails if the actual shell environment does not have these variables set.

### Root Cause Analysis
The `conftest.py` attempts to mock environment variables using a fixture `mock_env_vars`, but the application code is imported at the module level *before* the fixture can apply the mocks. This is a circular dependency between the test configuration and the application startup logic.

### Recommendation
1.  **Move Imports**: Delay importing `main` or `app` components inside `conftest.py` until within the fixtures where they are needed.
2.  **Use `pytest-env`**: Install `pytest-env` and configure `pytest.ini` to set default environment variables *before* collection starts.
3.  **Refactor Config**: Modify `get_settings()` to be lazy-loaded or allow missing values during test collection.

### Verification of Claims
-   **Dependencies**: `pytest-cov`, `coverage`, `pytest-asyncio` ARE installed correctly.
-   **Configuration**: `pytest.ini` is correct.
-   **Execution**: **FAILS** on fresh environment.

The "verified operational" status in previous reports likely relied on a `.env` file being present in the environment or cached pyc files, rather than a clean, reproducible test run.
