# CI — Bias Auditor | Technical Documentation

This GitHub Actions workflow automates continuous integration and deployment for the Bias Auditor project. It validates the Python backend and Node.js frontend in parallel, then publishes Docker images only after both checks succeed.

## Workflow Architecture

The pipeline is organized into three jobs so validation stays isolated and deployment remains gated by successful checks.

1. **Backend Quality Assurance** (`test-backend`).
   - Purpose: validates Python logic, style, and security across supported versions.
   - Environment: matrix build on Python 3.11 and 3.12.
   - Tooling: Ruff for linting and formatting checks, Pytest for unit and integration tests in `backend/tests/`.
   - Coverage: enforces an 80% minimum threshold; failing to meet it stops the pipeline.
   - Output: generates `coverage.xml` and uploads results to Codecov.

2. **Frontend Validation** (`build-frontend`).
   - Purpose: verifies that frontend assets compile correctly and meet TypeScript and build requirements.
   - Environment: Node.js 20.
   - Key command: `npm run build`, which catches syntax errors and broken imports before deployment.

3. **Docker Deployment** (`docker-deploy`).
   - Purpose: builds and pushes the Docker image set to Docker Hub.
   - Conditions: runs only when `test-backend` and `build-frontend` both pass, and the event is a push to `master`.
   - Technology: uses Docker Buildx and Docker Bake for concurrent, high-performance image builds.

## Infrastructure Requirements

The workflow depends on the following secrets and environment variables to remain configured.

| Name | Type | Description |
|---|---|---|
| `CODECOV_TOKEN` | Secret | Uploads test metrics to the Codecov dashboard. |
| `DOCKERHUB_USERNAME` | Secret | Docker registry username used for authentication. |
| `DOCKERHUB_TOKEN` | Secret | Personal access token with write permissions. |
| `APP_PORT` | Env | Port used by Uvicorn, defaulting to `8000`. |

## Deployment Settings

The images are built from the configuration in `docker-bake.hcl` or a similar Bake file, which defines the build targets and runtime wiring. The application listens on `0.0.0.0:8000` inside the container, exposes port `8000`, and is referenced locally at `http://127.0.0.1:8000`.

## Troubleshooting

- Build failures usually point to the frontend typecheck or dependency resolution step. Because `npm ci` installs exact lockfile versions, verify that `package-lock.json` is current if installation fails.
- Test failures occur when coverage drops below 80%; review the `pytest-cov` output in the workflow logs and the uploaded coverage report.
- Docker failures typically come from authentication or bake configuration issues. Confirm that `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are passed correctly to the Bake and push steps.