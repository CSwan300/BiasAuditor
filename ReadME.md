# ⚖️ Bias Auditor

A professional-grade fairness and disparity analysis tool for auditing datasets for algorithmic bias. The application evaluates how protected characteristics such as age, race, or gender affect prediction outcomes using the **Four-Fifths (80%) Rule**, a standard threshold used by legal and regulatory bodies.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- A modern web browser such as Chrome, Firefox, or Edge

### 2. Backend Setup

Install the Python dependencies from the project root:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup

Open `frontend/index.html` directly in your browser.

---

## 🛠 Features

- **Automated characteristic detection:** Automatically identifies protected columns such as age, gender, ethnicity, race, and sex.
- **Predictive outcome analysis:** Detects target variables such as prediction, result, label, and outcome to evaluate success rates across groups.
- **80% rule validation:** Flags potential adverse impact if a group’s selection rate falls below 80% of the highest-performing group.
- **Interactive visualisations:** Includes risk banners, disparity bar charts, and metadata tables.
- **Cross-format support:** Audits `.csv`, `.xlsx`, and `.xls` files.

---

## 📊 How the Audit Works

The tool uses the `BiasAuditor` class to carry out the analysis in a few stages:

1. **Data preprocessing:** Standardises column names and handles missing values.
2. **Age binning:** Automatically groups numeric age data into common demographic bands such as 18-29 and 30-44.
3. **Disparity calculation:** Computes the disparate impact ratio and the maximum disparity gap.
4. **Risk scoring:** Assigns a risk level of Low, Moderate, High, or Critical based on the share of characteristics that fail the 80% rule.

The analysis relies on pandas for grouping, aggregation, and Excel/CSV loading, which makes the statistical logic readable and dependable [web:3].

---

## 📂 Project Structure

```text
├── backend/
│   ├── auditor.py   # Core BiasAuditor logic and calculations
│   └── main.py      # FastAPI routes and file handling
├── frontend/
│   ├── index.html   # Main dashboard structure
│   ├── style.css    # UI styling
│   └── script.js    # API integration and dynamic rendering
└── requirements.txt # Python dependencies
```

---

## 📋 Data Requirements

For the auditor to work correctly, the dataset should include:

| Column Type | Example Column Names | Data Format |
| --- | --- | --- |
| **Protected** | `age`, `gender`, `ethnicity`, `race`, `sex` | String, category, or numeric for age |
| **Outcome** | `prediction`, `label`, `outcome`, `target` | Binary values or numeric scores |

**Sample row:**

```json
{"age": 28, "gender": "Non-binary", "ethnicity": "Asian", "prediction": 1}
```

---

## ⚖️ Legal Disclaimer

Bias Auditor is intended for internal fairness monitoring only. While it uses standard metrics such as the 80% rule, a low-risk result does not guarantee legal compliance, and a high-risk result does not automatically prove illegal discrimination. Always consult legal and ethics experts when interpreting algorithmic fairness results.

---

## Tech Choices

### Backend Framework

FastAPI was chosen for the backend because this application works heavily with structured data. It accepts uploaded files and returns JSON audit results, so strong validation and clear data models are important. FastAPI handles this naturally through built-in type checking and automatic API documentation, which makes development and testing easier [web:1][web:4]. Flask would need extra extensions to offer the same experience, while Django would add features such as an ORM, templating, and an admin panel that are unnecessary for a stateless file-processing API.

### Server Choice

Uvicorn was chosen because FastAPI runs on ASGI, and Uvicorn is an ASGI server built for that model [web:2][web:8]. That makes it a better fit than a traditional WSGI-only server for this application. It also keeps the deployment setup simple while still leaving room to scale if processing demand grows.

### Data Processing

Pandas was used for the audit calculations because it is well suited to working with tabular data, grouping rows, and reading both CSV and Excel files [web:3][web:6]. The bias checks in this project depend on clean, readable statistical logic, so pandas offers a practical balance of reliability and familiarity. Faster alternatives exist, but pandas keeps the implementation easier to understand and maintain.

### Excel Support

Openpyxl was included to support modern `.xlsx` files. It is the appropriate choice for current Excel formats and works well with pandas for spreadsheet ingestion. That makes it more suitable than older libraries that no longer support modern Excel files.

### Frontend Delivery

Nginx was used to serve the frontend because the interface is only a small set of static files. A full application server would be unnecessary overhead for that role. Nginx is lightweight and also works well as a reverse proxy for the backend, keeping responsibilities clearly separated.

### Containerisation

Docker was configured with a multi-stage build so the backend and frontend stay independent. This keeps each image focused on only what it needs, which reduces image size and avoids shipping unnecessary dependencies. It also makes it easier to update or scale the services separately.

### Frontend Approach

The frontend was built with plain JavaScript because its job is simple: upload a file, call the API, and render the results. Using React or Vue would add build tooling and framework overhead without providing much value for such a small interface. Keeping it vanilla also makes local development easier because the HTML file can be opened directly in a browser without a build step.

---

## 👨‍💻 Author / Acknowledgements

- **Google Gemini** — for assistance with the README draft
- **cswan300** — [GitHub Profile](https://github.com/cswan300)
