# ⚖️ Bias Auditor

A professional-grade fairness and disparity analysis tool for auditing datasets for algorithmic bias. The application evaluates how protected characteristics such as age, race, or gender affect prediction outcomes using the **Four-Fifths (80%) Rule**, a standard threshold used by legal and regulatory bodies.

## 🚀 Quick Start (Dockerized)

The easiest way to run the full stack (FastAPI Backend + React Frontend) is using Docker Compose.

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- or just docker 

### 2. Launch the System
Navigate to the project root and run:

```bash
docker-compose up --build
```

### 3. Access the Dashboard
- Frontend UI: [http://localhost:8080](http://localhost:8080)
- Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🏗 Why This Architecture?

### Backend: Python & Pandas (Core Logic)
The backend was built using Python and Pandas because they are the industry standard for data science and algorithmic fairness.

- Statistical Rigor: The `BiasAuditor` class provides a centralized, tested environment for calculating the Disparate Impact Ratio (DIR) and Max Disparity Gaps.
- Scalability: By using an Object-Oriented approach for the auditor logic, new fairness metrics can be added without rewriting the API or UI.
- Separation of Concerns: The backend handles the heavy computational lifting and data binning, serving only the final, lightweight JSON results to the frontend.

### Frontend: React + TypeScript (Modularity)
The frontend was migrated from vanilla JavaScript to React 18 with TypeScript to ensure the tool meets enterprise standards for reliability and modularity.

- Encapsulated Modularity: Visual elements like the `AuditCard` and `RiskBanner` are now independent, reusable modules. This separation allows easier debugging and the ability to scale the UI without code duplication.
- Type Safety: TypeScript provides a robust interface layer between the Python backend and the UI. By defining strict types for the `AuditResponse`, the UI handles backend data predictably and avoids many runtime errors.
- Maintainability: Modern state management allows the dashboard to update dynamically as datasets are uploaded, providing a seamless, app-like experience.

## 🛠 Features

- Automated characteristic detection: Automatically identifies protected columns such as age, gender, ethnicity, race, and sex.
- Predictive outcome analysis: Detects target variables such as prediction and label to evaluate success rates across groups.
- 80% rule validation: Flags potential adverse impact if a group’s selection rate falls below 80% of the highest-performing group.
- High-Fidelity Dashboard: Features a modern UI with animated progress bars, risk rings, and real-time disparity flagging.
- Cross-format support: Audits `.csv`, `.xlsx`, and `.xls` files.

## 📊 How the Audit Works

The tool uses the `BiasAuditor` class to carry out the analysis in a few stages:

- Data preprocessing: Standardises column names and handles missing values.
- Age binning: Automatically groups numeric age data into common demographic bands such as 18-29 and 30-44.
- Disparity calculation: Computes the disparate impact ratio:

$$
DIR = \frac{\text{Selection Rate of Protected Group}}{\text{Selection Rate of Reference Group}}
$$

- Risk scoring: Assigns a risk level of Low, Moderate, High, or Critical based on the share of characteristics that fail the 80% rule.

## 📂 Project Structure

```text
├── backend/
│   ├── auditor.py       # Core BiasAuditor logic and math
│   └── main.py          # FastAPI routes and file handling
├── frontend/
│   ├── src/
│   │   ├── components/  # Modular React components (AuditCard, RiskBanner)
│   │   ├── styles/      # Global and component-specific CSS
│   │   ├── types.ts     # TypeScript interfaces for API responses
│   │   └── App.tsx      # Main application logic
│   └── vite.config.ts   # Frontend build configuration
├── Dockerfile           # Multi-stage build (Frontend Build -> Nginx/Python)
├── docker-compose.yml   # Orchestration for the full stack
└── requirements.txt     # Python dependencies
```

## 📋 Data Requirements

For the auditor to work correctly, the dataset should include:

| Column Type | Example Column Names | Data Format |
|-------------|----------------------|-------------|
| Protected | `age`, `gender`, `ethnicity`, `race`, `sex` | String, category, or numeric for age |
| Outcome | `prediction`, `label`, `outcome`, `target` | Binary values or numeric scores |

## ⚖️ Legal Disclaimer

Bias Auditor is intended for internal fairness monitoring only. While it uses standard metrics such as the 80% rule, a low-risk result does not guarantee legal compliance, and a high-risk result does not automatically prove illegal discrimination. Always consult legal and ethics experts when interpreting algorithmic fairness results.

## 👨‍💻 Author / Acknowledgements

- Google Gemini — AI Collaboration & Technical Architecture
- [cswan300 — GitHub Profile](https://github.com/cswan300)