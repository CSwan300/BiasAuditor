# ⚖️ BiasAuditor

> A full-stack algorithmic fairness auditing tool built with Python, FastAPI, React 18, TypeScript, and Docker.

| | |
|---|---|
| **Repository** | [github.com/CSwan300/BiasAuditor](https://github.com/CSwan300/BiasAuditor) |
| **Stack** | Python · FastAPI · Pandas · SciPy · ReportLab · React 18 · TypeScript · Docker · Nginx · GitHub Actions |
| **Backend Test Coverage** | 96% (recheck after recent additions) |
| **Status** | Active — Personal / ESG Risk Project, 2026 |

---

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start](#2-quick-start)
3. [Architecture & Technology Decisions](#3-architecture--technology-decisions)
4. [How the Audit Works](#4-how-the-audit-works)
5. [PDF Report Output](#5-pdf-report-output)
6. [Project Structure](#6-project-structure)
7. [Data Requirements](#7-data-requirements)
8. [Limitations](#8-limitations)
9. [Possible Future Updates](#9-possible-future-updates)
10. [Legal Disclaimer](#10-legal-disclaimer)

---

## 1. Overview

BiasAuditor is a fairness and disparity analysis tool that lets you upload a dataset and immediately understand whether a predictive model treats all demographic groups equitably. It applies the **Four-Fifths (80%) Rule** — a threshold used by the U.S. Equal Employment Opportunity Commission (EEOC) and other regulatory bodies — alongside **Disparate Impact Ratios (DIR)** to produce structured, tiered risk scores across every detected protected characteristic.

Each flagged disparity is now also tested for **statistical significance**, and the tool generates **automated mitigation suggestions** (sample reweighting, synthetic data generation, decision-threshold calibration) for any characteristic that fails the audit — moving the project from a pure detection tool toward something closer to a governance decision-support tool. Results can be exported as a structured **PDF report** for sharing with compliance or legal stakeholders.

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
| Backend health check | http://localhost:8000/health |

To stop all services: `docker-compose down`

---

## 3. Architecture & Technology Decisions

Each technology in this stack was chosen deliberately. This section explains not just *what* was used, but *why* — and what alternatives were considered.

### 3.1 Backend — Python, FastAPI & SciPy

**Python** was chosen as the backend language because it is the de facto standard for data science and statistical computing. The key library is **Pandas**, which provides vectorised DataFrame operations that make column-level disparity calculations both readable and performant on datasets of typical HR or audit size (thousands to hundreds of thousands of rows).

**FastAPI** was selected as the web framework over the alternatives for three reasons:

- **Performance:** FastAPI is built on Starlette and uses async I/O, making it significantly faster than Flask for I/O-bound tasks like file uploads.
- **Automatic documentation:** FastAPI generates interactive OpenAPI (Swagger) docs from type hints alone, which is valuable for demonstrating the API.
- **Data validation:** Pydantic models, built into FastAPI, validate incoming request data automatically and produce clear error messages.

*Why not Flask?* Flask is simpler and more familiar to beginners, but it lacks native async support and requires third-party libraries (Flask-RESTful, Marshmallow) to achieve what FastAPI provides out of the box.

**SciPy** (`scipy.stats`) was added to move disparity detection beyond a single fixed ratio. Fisher's exact test and a chi-squared test of independence are used to check whether an observed disparity is statistically significant rather than an artefact of a small sample — see [4.4](#44-statistical-significance-testing).

The core logic lives in a single `BiasAuditor` class (`auditor.py`). The object-oriented design means new fairness metrics can be added as methods without touching the API layer — an application of the **Open/Closed Principle** from SOLID design.

### 3.2 Frontend — React 18 + TypeScript

The frontend was originally written in vanilla JavaScript and was migrated to **React 18 with TypeScript**.

**React** was chosen because the dashboard is inherently component-driven: a `RiskBanner`, a set of `AuditCard`s, a disparity chart, and a file uploader are all independent pieces of UI with their own state. React's component model makes this separation natural. With vanilla JS, managing DOM updates imperatively as audit results arrived became increasingly fragile.

**TypeScript** was added to introduce a strict interface between the Python backend and the JavaScript frontend. By defining the `AuditResponse` type to match the JSON the API returns, the compiler catches mismatches at build time rather than at runtime in a user's browser. For a tool that processes sensitive data and presents legal-adjacent risk scores, correctness matters.

*Why not Vue.js?* Vue has a gentler learning curve and excellent single-file component support, but React's ecosystem and TypeScript integration are more mature, and React + TypeScript is a more widely recognised combination in industry.

**Vite** was used as the build tool instead of Create React App (CRA). CRA is deprecated and slow; Vite provides near-instant hot module replacement and a significantly faster build pipeline.

### 3.3 Containerisation — Docker & Docker Compose

The **multi-stage Dockerfile** first builds the React app using a Node.js image, then copies the compiled static files into a lightweight Nginx image alongside the Python backend. The final container does not include Node.js at runtime, keeping the image size small.

**Docker Compose** orchestrates the two services and handles the network between them. Without containerisation, a reviewer cloning the repo would need to manually install Python, Node.js, and configure CORS. With Docker, the entire stack starts with a single command — standard practice for any real-world project.

**Nginx** acts as a reverse proxy: it serves the static React build on port 8080 and forwards `/api/*` requests to the FastAPI backend on port 8000. This mirrors how production deployments work (behind a load balancer or on a cloud provider), rather than running both services directly on exposed ports.

A lightweight **`/health`** endpoint reports backend status for Docker/Kubernetes liveness and readiness probes, so an orchestrator can detect a stalled backend without hitting the main audit logic.

### 3.4 Testing — pytest & 96% Coverage

All backend tests are written using **pytest**. Tests cover the `BiasAuditor` class directly (unit tests) and the FastAPI endpoints via the `httpx` test client (integration tests).

Coverage is measured with **pytest-cov** and reported in the CI pipeline. Coverage was last measured at **96%** before the significance-testing, mitigation, and PDF-reporting modules were added — worth re-running before quoting this figure anywhere, since new branches (PDF generation, mitigation suggestion logic) need their own test coverage to keep that number honest.

**AI-assisted test generation** was used to accelerate writing boilerplate test cases, particularly for edge cases like empty datasets, single-group characteristics, and malformed file uploads. The generated tests were reviewed, corrected where necessary, and integrated into the suite.

### 3.5 CI/CD — GitHub Actions

A **GitHub Actions** workflow runs on every push to `master`. It installs dependencies, runs the full test suite, and reports coverage, ensuring the main branch is never in a broken state and that coverage regressions are caught immediately.

*Why not CircleCI or Travis CI?* GitHub Actions is free for public repositories, natively integrated with GitHub, and requires no separate account or configuration.

### 3.6 PDF Reporting — ReportLab

Audit results can be exported as a downloadable PDF via the `/report/pdf` endpoint. **ReportLab** was chosen because it builds PDFs programmatically from Python objects (`Paragraph`, `Table`, `Drawing`) rather than requiring an HTML-to-PDF rendering step, which keeps the dependency footprint small inside the existing Docker image.

Each report includes an organisation name, the fairness threshold applied, an overall colour-coded risk status (green / amber / red), and a per-characteristic bar chart built with `reportlab.graphics.charts.barcharts.VerticalBarChart`, showing selection rate by group. The PDF is streamed directly to the client via FastAPI's `StreamingResponse`, so no temporary file is written to disk.

---

## 4. How the Audit Works

### 4.1 Protected Characteristic Detection

The tool scans column names (after lowercasing and stripping whitespace) against a predefined list of protected characteristic keywords: `age`, `gender`, `sex`, `race`, `ethnicity`, `nationality`. If no keyword columns are found, it falls back to a secondary heuristic: any categorical column with a low-to-moderate number of unique values relative to the dataset size (more than 1, fewer than 5% of total rows) is offered as a candidate protected characteristic, to catch columns with non-standard names. This is still a heuristic rather than true semantic detection — see [Limitations](#8-limitations).

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

The fairness threshold is **user-configurable** at request time (passed as `fairness_threshold` on the `/audit` and `/report/pdf` endpoints, accepted as either a decimal like `0.8` or a percentage like `80`) rather than fixed. A DIR below the configured threshold (defaulting to **0.8**, the standard Four-Fifths Rule) triggers the adverse impact flag for that group. A DIR of 1.0 means perfect equality with the reference group.

### 4.4 Statistical Significance Testing

Every comparison between the reference group (the group with the highest selection rate) and each other group is additionally tested for statistical significance, rather than relying on the raw ratio alone:

- **Fisher's exact test** is used when the combined sample for the two groups is small.
- A **chi-squared test of independence** is used otherwise.
- A result is marked statistically significant (`stat_sig`) at **p < 0.05**.

This means a disparity ratio computed from a handful of data points is distinguishable from one backed by a large, robust sample — directly addressing the risk of over-interpreting small-sample disparities.

### 4.5 Risk Scoring

After computing DIRs and significance flags for all groups across all characteristics, the percentage of characteristics with at least one flagged group determines the overall risk level:

| Risk Level | Condition |
|---|---|
| Low | 0% of characteristics flag adverse impact |
| Moderate | Up to 25% of characteristics flag adverse impact |
| High | Up to 60% of characteristics flag adverse impact |
| Critical | Over 60% of characteristics flag adverse impact |

A numeric risk score (0–100) is also calculated from the most severe disparity ratio found across all audited characteristics.

### 4.6 Automated Mitigation Suggestions

For any characteristic that fails the audit, BiasAuditor now generates a ranked list of suggested next steps rather than just reporting the failure:

- **Sample reweighting** (high priority) — assigns higher training weight to underrepresented groups whose selection rate falls below the threshold relative to the best-performing group.
- **Synthetic data generation (SMOTE)** (medium priority) — suggested specifically when the smallest underrepresented group has fewer than 500 records, flagging that the disparity result may also be a data-volume problem.
- **Decision threshold calibration** (lower priority) — suggested generally, as a way to adjust the model's decision boundary for underrepresented groups to improve parity.

Groups below a configurable minimum size (`MIN_GROUP_SIZE`) are excluded from the reweighting calculation, so the suggestion engine doesn't recommend reweighting a group that's too small to reweight meaningfully.

---

## 5. PDF Report Output

Calling `/report/pdf` with the same parameters as `/audit` returns a downloadable PDF (`bias_audit_YYYYMMDD.pdf`) containing:

- Organisation name and the fairness threshold that was applied.
- An overall risk status banner, colour-coded green (low), amber (moderate), or red (high/critical).
- One section per audited characteristic, each showing a PASS/FLAGGED status and a bar chart of selection rate by group.

This is intended as a shareable artefact for non-technical stakeholders — compliance, legal, or HR teams who need the headline result without reading raw JSON.

---

## 6. Project Structure

```
BiasAuditor/
├── .github/
│   └── workflows/                  # GitHub Actions CI pipeline
├── backend/
│   ├── config.py                   # Shared config (e.g. MIN_GROUP_SIZE)
│   ├── main.py                     # FastAPI app: routes, file parsing, CORS config
│   └── modules/
│       ├── AuditLogic/
│       │   └── auditor.py          # BiasAuditor class — fairness maths + significance testing
│       └── Build_pdf/
│           ├── mitigation.py       # suggest_mitigation — automated mitigation suggestions
│           ├── pdf_builder.py      # generate_pdf_content, create_bar_chart (ReportLab)
│           └── reporting.py        # build_pdf_response — streams the PDF back to the client
├── frontend/
│   ├── src/
│   │   ├── components/             # AuditCard, RiskBanner, FileUploader, etc.
│   │   ├── styles/                 # Global and component-level CSS
│   │   ├── types.ts                # TypeScript interfaces (AuditResponse, etc.)
│   │   └── App.tsx                 # Root component and application state
│   └── vite.config.ts              # Vite build configuration
├── tests/                          # pytest test suite
├── sample-data/                    # Example datasets for testing
├── Dockerfile                      # Multi-stage build (React → Nginx + Python)
├── docker-compose.yml              # Service orchestration
├── nginx.conf                      # Reverse proxy configuration
└── requirements.txt                # Python dependencies
```

---

## 7. Data Requirements

Your dataset needs at least one **protected characteristic** column and one **binary outcome** column.

| Column Type | Accepted Names | Format |
|---|---|---|
| Protected characteristic | `age`, `gender`, `sex`, `race`, `ethnicity`, `nationality` | String, category, or numeric (age only) |
| Outcome / prediction | `prediction`, `label`, `outcome`, `target`, `result` | Binary (0/1) or numeric score |

**Example row:**
```json
{ "age": 34, "gender": "Female", "ethnicity": "Asian", "prediction": 1 }
```

Sample datasets covering employment, lending, and admissions scenarios are included in the [`sample-data/`](./sample-data) directory.

---

## 8. Limitations

Being honest about a tool's limitations is as important as documenting its features.

- **Keyword + heuristic column detection, not semantic detection.** Beyond the fixed keyword list, additional candidate columns are surfaced using a cardinality heuristic (low-to-moderate unique value count), not true semantic understanding of what a column represents. It can still miss or mis-suggest columns with unusual names or value distributions.

- **The 80% Rule is a heuristic, not law.** Failing the Four-Fifths threshold is not proof of illegal discrimination, and passing it is not proof of compliance. The rule is a screening tool that triggers further investigation, not a definitive legal test — even with significance testing layered on top.

- **No intersectionality analysis in the live audit.** Each protected characteristic is still audited independently (e.g., gender alone, age alone), not as compound groups (e.g., Black women, older men), where some of the most significant real-world disparities occur.

- **Binary outcome assumption.** The DIR calculation assumes a binary or near-binary outcome. Continuous scores are supported but treated as-is, which may not be appropriate for all use cases.

- **Significance testing covers individual disparities, not the overall risk score.** Statistical significance is calculated per group comparison, but the overall risk level and score are still driven by the raw DIR values rather than only counting statistically significant disparities — a characteristic can still drive the risk score up from a disparity that wasn't statistically significant.

- **Minimum group size is applied to mitigation suggestions, not to the audit itself.** `MIN_GROUP_SIZE` filters which groups are eligible for reweighting suggestions, but small groups are still included in the core DIR calculation and risk scoring without a separate warning.

---

## 9. Possible Future Updates

### Fairness Metrics

- **Intersectional analysis** — Audit compound demographic groups (gender × ethnicity) to surface disparities that per-characteristic analysis misses.
- **Risk-score-level significance weighting** — Factor statistical significance into the overall risk score and level, not just into the per-group detail.
- **Additional fairness criteria** — Implement Equalised Odds, Calibration, and Predictive Parity, which capture fundamentally different notions of what "fair" means and are widely discussed in the academic literature.

### Data Handling

- **True semantic column detection** — Use fuzzy string matching or a small classifier to detect protected characteristics from column names that don't match the keyword list or the cardinality heuristic.
- **Minimum sample size warnings at the audit level** — Surface an explicit warning on any flagged group below `MIN_GROUP_SIZE`, rather than only excluding it from mitigation suggestions.
- **Data preview** — Show a sample of the uploaded dataset before running the audit, so users can confirm the tool has interpreted their columns correctly.

### Infrastructure & UX

- **Persistent audit history** — Store previous audit results in a database (SQLite or PostgreSQL) so analysts can compare results over time as datasets are updated.
- **CSV/JSON export alongside PDF** — Offer machine-readable export formats for analysts who want to pull results into other tooling.
- **Authentication** — Add user accounts so multiple analysts in an organisation can use the tool without sharing a single instance.
- **Real-time progress indicator** — For large datasets, show processing progress rather than a static loading spinner.

---

## 10. Legal Disclaimer

> BiasAuditor is intended for **internal fairness monitoring only**. A low-risk result does not guarantee legal compliance, and a high-risk result does not automatically prove illegal discrimination. The Four-Fifths Rule is a screening heuristic, not a legal standard. Statistical significance testing indicates whether an observed disparity is likely due to chance, not whether it is legally actionable. Always consult qualified legal and ethics professionals before drawing compliance conclusions from algorithmic fairness analysis.

---

## Author

**CSwan300** — [github.com/CSwan300](https://github.com/CSwan300)
