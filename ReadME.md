# ⚖️ BiasAuditor

> A full-stack algorithmic fairness auditing tool built with Python, FastAPI, React 18, TypeScript, and Docker.

| | |
|---|---|
| **Repository** | [github.com/CSwan300/BiasAuditor](https://github.com/CSwan300/BiasAuditor) |
| **Stack** | Python · FastAPI · Pandas · React 18 · TypeScript · Docker · Nginx · GitHub Actions |
| **Backend Test Coverage** | 96% |
| **Status** | Active — Personal / ESG Risk Project, 2026 |

---

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start](#2-quick-start)
3. [Architecture & Technology Decisions](#3-architecture--technology-decisions)
4. [How the Audit Works](#4-how-the-audit-works)
5. [Project Structure](#5-project-structure)
6. [Data Requirements](#6-data-requirements)
7. [Limitations](#7-limitations)
8. [Possible Future Updates](#8-possible-future-updates)
9. [Legal Disclaimer](#9-legal-disclaimer)

---

## 1. Overview

BiasAuditor is a fairness and disparity analysis tool that lets you upload a dataset and immediately understand whether a predictive model treats all demographic groups equitably. It applies the **Four-Fifths (80%) Rule** — a threshold used by the U.S. Equal Employment Opportunity Commission (EEOC) and other regulatory bodies — alongside **Disparate Impact Ratios (DIR)** to produce structured, tiered risk scores across every detected protected characteristic.

The project was built as a personal project to explore the intersection of data science, software engineering, and ethical AI. It intentionally mirrors the architecture of a production tool: a stateless REST API backend, a modern TypeScript frontend, containerised deployment, and an automated CI/CD pipeline.

---

## 2. Quick Start

The easiest way to run the full stack is with Docker Compose, which starts the FastAPI backend and React frontend together, wired through an Nginx reverse proxy.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) and Git.

```bash
# Clone the repository
git clone https://github.com/CSwan300/BiasAuditor.git
cd BiasAuditor

# Build and launch all services
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend UI | http://localhost:8080 |
| Backend API docs (Swagger) | http://localhost:8000/docs |

To stop all services: `docker-compose down`

---

## 3. Architecture & Technology Decisions

Each technology in this stack was chosen deliberately. This section explains not just *what* was used, but *why* — and what alternatives were considered.

### 3.1 Backend — Python & FastAPI

**Python** was chosen as the backend language because it is the de facto standard for data science and statistical computing. The key library is **Pandas**, which provides vectorised DataFrame operations that make column-level disparity calculations both readable and performant on datasets of typical HR or audit size (thousands to hundreds of thousands of rows).

**FastAPI** was selected as the web framework over the alternatives for three reasons:

- **Performance:** FastAPI is built on Starlette and uses async I/O, making it significantly faster than Flask for I/O-bound tasks like file uploads.
- **Automatic documentation:** FastAPI generates interactive OpenAPI (Swagger) docs from type hints alone, which is valuable for demonstrating the API.
- **Data validation:** Pydantic models, built into FastAPI, validate incoming request data automatically and produce clear error messages.

*Why not Flask?* Flask is simpler and more familiar to beginners, but it lacks native async support and requires third-party libraries (Flask-RESTful, Marshmallow) to achieve what FastAPI provides out of the box.

The core logic lives in a single `BiasAuditor` class (`auditor.py`). The object-oriented design means new fairness metrics can be added as methods without touching the API layer — an application of the **Open/Closed Principle** from SOLID design.

---

### 3.2 Frontend — React 18 + TypeScript

The frontend was originally written in vanilla JavaScript and was migrated to **React 18 with TypeScript**.

**React** was chosen because the dashboard is inherently component-driven: a `RiskBanner`, a set of `AuditCard`s, a disparity chart, and a file uploader are all independent pieces of UI with their own state. React's component model makes this separation natural. With vanilla JS, managing DOM updates imperatively as audit results arrived became increasingly fragile.

**TypeScript** was added to introduce a strict interface between the Python backend and the JavaScript frontend. By defining the `AuditResponse` type to match the JSON the API returns, the compiler catches mismatches at build time rather than at runtime in a user's browser. For a tool that processes sensitive data and presents legal-adjacent risk scores, correctness matters.

*Why not Vue.js?* Vue has a gentler learning curve and excellent single-file component support, but React's ecosystem and TypeScript integration are more mature, and React + TypeScript is a more widely recognised combination in industry.

**Vite** was used as the build tool instead of Create React App (CRA). CRA is deprecated and slow; Vite provides near-instant hot module replacement and a significantly faster build pipeline.

---

### 3.3 Containerisation — Docker & Docker Compose

The **multi-stage Dockerfile** first builds the React app using a Node.js image, then copies the compiled static files into a lightweight Nginx image alongside the Python backend. The final container does not include Node.js at runtime, keeping the image size small.

**Docker Compose** orchestrates the two services and handles the network between them. Without containerisation, a reviewer cloning the repo would need to manually install Python, Node.js, and configure CORS. With Docker, the entire stack starts with a single command — standard practice for any real-world project.

**Nginx** acts as a reverse proxy: it serves the static React build on port 8080 and forwards `/api/*` requests to the FastAPI backend on port 8000. This mirrors how production deployments work (behind a load balancer or on a cloud provider), rather than running both services directly on exposed ports.

---

### 3.4 Testing — pytest & 96% Coverage

All backend tests are written using **pytest**. Tests cover the `BiasAuditor` class directly (unit tests) and the FastAPI endpoints via the `httpx` test client (integration tests).

Coverage is measured with **pytest-cov** and reported in the CI pipeline. The current backend coverage is **96%**. The remaining 4% consists primarily of defensive error-handling branches that are difficult to trigger through normal inputs — a common characteristic of high-coverage codebases.

**AI-assisted test generation** was used to accelerate writing boilerplate test cases, particularly for edge cases like empty datasets, single-group characteristics, and malformed file uploads. The generated tests were reviewed, corrected where necessary, and integrated into the suite.

---

### 3.5 CI/CD — GitHub Actions

A **GitHub Actions** workflow runs on every push to `master`. It installs dependencies, runs the full test suite, and reports coverage, ensuring the main branch is never in a broken state and that coverage regressions are caught immediately.

*Why not CircleCI or Travis CI?* GitHub Actions is free for public repositories, natively integrated with GitHub, and requires no separate account or configuration.

---

## 4. How the Audit Works

### 4.1 Protected Characteristic Detection

The tool scans column names (after lowercasing and stripping whitespace) against a predefined list of protected characteristic keywords: `age`, `gender`, `sex`, `race`, `ethnicity`. This is a keyword-matching heuristic — it will miss columns named `protected_group` or `demographic_segment`. See [Section 8](#8-possible-future-updates) for how this could be improved.

### 4.2 Age Binning

Numeric age columns are automatically grouped into standard demographic bands:

| Band | Range |
|---|---|
| Young Adult | 18–29 |
| Adult | 30–44 |
| Mid-Career | 45–59 |
| Senior | 60+ |

The bin boundaries used here are common in HR and employment analytics but are not universal. Different regulatory contexts may require different groupings — for example, the Age Discrimination in Employment Act (ADEA) primarily protects workers aged 40 and over.

### 4.3 Disparate Impact Ratio (DIR)

The DIR is the core fairness metric:

```
DIR = Selection Rate of Group  ÷  Selection Rate of Highest-Performing Group

Selection Rate = (Positive outcomes in group) ÷ (Total members of group)
```

A DIR below **0.8** triggers the adverse impact flag under the Four-Fifths Rule. A DIR of 1.0 means perfect equality with the reference group.

### 4.4 Risk Scoring

After computing DIRs for all groups across all characteristics, the percentage of characteristics with at least one flagged group determines the overall risk level:

| Risk Level | Condition |
|---|---|
| 🟢 Low | 0% of characteristics flag adverse impact |
| 🟡 Moderate | 1–33% of characteristics flag adverse impact |
| 🔴 High | 34–66% of characteristics flag adverse impact |
| ⚫ Critical | 67–100% of characteristics flag adverse impact |

---

## 5. Project Structure

```
BiasAuditor/
├── .github/
│   └── workflows/          # GitHub Actions CI pipeline
├── backend/
│   ├── auditor.py          # BiasAuditor class — all fairness logic and maths
│   └── main.py             # FastAPI app: routes, file parsing, CORS config
├── frontend/
│   ├── src/
│   │   ├── components/     # AuditCard, RiskBanner, FileUploader, etc.
│   │   ├── styles/         # Global and component-level CSS
│   │   ├── types.ts        # TypeScript interfaces (AuditResponse, etc.)
│   │   └── App.tsx         # Root component and application state
│   └── vite.config.ts      # Vite build configuration
├── tests/                  # pytest test suite (96% backend coverage)
├── sample-data/            # Example datasets for testing
├── Dockerfile              # Multi-stage build (React → Nginx + Python)
├── docker-compose.yml      # Service orchestration
├── nginx.conf              # Reverse proxy configuration
└── requirements.txt        # Python dependencies
```

---

## 6. Data Requirements

Your dataset needs at least one **protected characteristic** column and one **binary outcome** column.

| Column Type | Accepted Names | Format |
|---|---|---|
| Protected characteristic | `age`, `gender`, `sex`, `race`, `ethnicity` | String, category, or numeric (age only) |
| Outcome / prediction | `prediction`, `label`, `outcome`, `target`, `result` | Binary (0/1) or numeric score |

**Example row:**
```json
{ "age": 34, "gender": "Female", "ethnicity": "Asian", "prediction": 1 }
```

Sample datasets covering employment, lending, and admissions scenarios are included in the [`sample-data/`](./sample-data) directory.

---

## 7. Limitations

Being honest about a tool's limitations is as important as documenting its features.

- **Keyword-based column detection.** Protected characteristic detection relies on column name matching. Columns with non-standard names (e.g., `protected_attr`, `group_id`) will not be detected automatically and must be renamed before uploading.

- **The 80% Rule is a heuristic, not law.** Failing the Four-Fifths threshold is not proof of illegal discrimination, and passing it is not proof of compliance. The rule is a screening tool that triggers further investigation, not a definitive legal test.

- **No intersectionality analysis.** The tool audits each characteristic independently (e.g., gender alone, age alone). It does not examine compound groups (e.g., Black women, older men), where some of the most significant real-world disparities occur.

- **Binary outcome assumption.** The DIR calculation assumes a binary or near-binary outcome. Continuous scores are supported but treated as-is, which may not be appropriate for all use cases.

- **Small sample sensitivity.** The 80% Rule can produce misleading results with small group sizes. A group with 2 members and 1 positive outcome has a 50% selection rate — statistically fragile. The tool does not currently flag groups below a minimum sample size threshold.

- **Static threshold.** The 0.8 DIR threshold is fixed. Some regulatory contexts use different thresholds or apply statistical significance tests (e.g., Fisher's exact test, Z-test for proportions) instead of or in addition to the 80% Rule.

---

## 8. Possible Future Updates

### Fairness Metrics

- **Intersectional analysis** — Audit compound demographic groups (gender × ethnicity) to surface disparities that per-characteristic analysis misses.
- **Statistical significance testing** — Add Fisher's exact test or a Z-test for proportions alongside the DIR, so small-sample results are flagged with appropriate uncertainty.
- **Additional fairness criteria** — Implement Equalised Odds, Calibration, and Predictive Parity, which capture fundamentally different notions of what "fair" means and are widely discussed in the academic literature.
- **Configurable thresholds** — Allow users to set a custom DIR threshold (e.g., 0.9 for stricter standards) rather than hardcoding 0.8.

### Data Handling

- **Semantic column detection** — Use fuzzy string matching or a small classifier to detect protected characteristics from column names that don't exactly match the keyword list.
- **Minimum sample size warnings** — Flag any group with fewer than N members (configurable, default 30) to warn the user that its statistics may be unreliable.
- **Data preview** — Show a sample of the uploaded dataset before running the audit, so users can confirm the tool has interpreted their columns correctly.

### Infrastructure & UX

- **Persistent audit history** — Store previous audit results in a database (SQLite or PostgreSQL) so analysts can compare results over time as datasets are updated.
- **Export to PDF / CSV** — Allow users to download the audit report in a format suitable for sharing with compliance or legal teams.
- **Authentication** — Add user accounts so multiple analysts in an organisation can use the tool without sharing a single instance.
- **Real-time progress indicator** — For large datasets, show processing progress rather than a static loading spinner.

---

## 9. Legal Disclaimer

> BiasAuditor is intended for **internal fairness monitoring only**. A low-risk result does not guarantee legal compliance, and a high-risk result does not automatically prove illegal discrimination. The Four-Fifths Rule is a screening heuristic, not a legal standard. Always consult qualified legal and ethics professionals before drawing compliance conclusions from algorithmic fairness analysis.

---

## Author

**CSwan300** — [github.com/CSwan300](https://github.com/CSwan300)
