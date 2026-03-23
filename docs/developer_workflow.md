# Developer Workflow & Quality Gates

## Local Development
The backend is designed for rapid local iteration. Use the provided automation scripts to ensure code quality before pushing.

### Prerequisites
- Python 3.10+
- Virtual Environment (`venv`) active

### Common Commands
| Task | Makefile (Linux/macOS) | PowerShell (Windows) |
| :--- | :--- | :--- |
| **Run App** | `make run` | `./scripts/dev.ps1 run` |
| **Run Tests** | `make test` | `./scripts/dev.ps1 test` |
| **Lint Code** | `make lint` | `./scripts/dev.ps1 lint` |
| **Format Code** | `make format` | `./scripts/dev.ps1 format` |

## Quality Gates

### 1. Formatting & Style
We use **Black** for deterministic formatting and **Ruff** for high-performance linting.
- **Rules**: PEP 8 compliance, sorted imports, and modern Python syntax (Py3.10+).
- **Enforcement**: Linting must pass without errors. Warnings should be addressed.

### 2. Testing
- **Unit Tests**: Focus on service logic (e.g., risk scoring formulas).
- **Integration Tests**: Focus on database interactions and API contracts using `fastapi.testclient`.
- **Coverage**: All new features must include corresponding tests in the `tests/` directory.

### 3. CI/CD Readiness
The backend is structured to be "CI-ready":
- All test commands return non-zero exit codes on failure.
- Configurations for linting and testing are centralized in `pyproject.toml` and `pytest.ini`.
- Mocks are used for external services (Vertex AI, MISP) to ensure tests can run in isolated environments without credentials.

## Deployment Note
Before production deployment, ensure:
1. All environment variables in `.env.example` are populated in the production environment.
2. The `MONGODB_URI` points to a secure, indexed instance.
3. Secure headers (from `app.core.security`) are actively reviewed for the specific hosting provider.
