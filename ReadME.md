
---

# ⚖️ Bias Auditor

A professional-grade Fairness & Disparity Analysis tool designed to audit datasets for algorithmic bias. This application evaluates how different protected characteristics (like age, race, or gender) impact prediction outcomes using the **Four-Fifths (80%) Rule**, a standard threshold used by legal and regulatory bodies.

## 🚀 Quick Start

### 1. Prerequisites

* Python 3.8+
* A modern web browser (Chrome, Firefox, Edge)

### 2. Backend Setup

Navigate to the project root and install the required Python dependencies:

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

* **Automated Characteristic Detection:** Automatically identifies protected columns (Age, Gender, Ethnicity, Race, Sex).
* **Predictive Outcome Analysis:** Detects target variables (Prediction, Result, Label, etc.) to evaluate success rates across groups.
* **80% Rule Validation:** Flags potential "Adverse Impact" if the selection rate for a group is less than 80% of the highest-performing group.
* **Interactive Visualizations:** High-fidelity risk banners, disparity bar charts, and data metadata tables.
* **Cross-Format Support:** Audit datasets in `.csv`, `.xlsx`, or `.xls` formats.

---

## 📊 How the Audit Works

The tool utilizes the `BiasAuditor` class to perform the following steps:

1. **Data Preprocessing:** Standardizes column names and handles missing values.
2. **Age Binning:** Automatically categorizes numeric age data into standard demographic brackets (e.g., 18-29, 30-44).
3. **Disparity Calculation:**
* **Disparate Impact Ratio (DIR):** Calculated as $DIR = \frac{\text{Lowest Group Rate}}{\text{Highest Group Rate}}$.
* **Max Disparity Gap:** The absolute difference between the highest and lowest group rates.


4. **Risk Scoring:** Assigns a risk level (Low, Moderate, High, Critical) based on the percentage of characteristics that fail the 80% rule.

---

## 📂 Project Structure

```text
├── backend/
│   ├── auditor.py   # Core BiasAuditor logic and math
│   └── main.py      # FastAPI routes and file handling
├── frontend/
│   ├── index.html   # Main dashboard structure
│   ├── style.css    # Cyber-grid UI design
│   └── script.js    # API integration and dynamic rendering
└── requirements.txt  # Python dependencies (pandas, fastapi, etc.)

```

---

## 📋 Data Requirements

For the auditor to function correctly, your dataset should include:

| Column Type | Example Column Names | Data Format |
| --- | --- | --- |
| **Protected** | `age`, `gender`, `ethnicity`, `race`, `sex` | String/Category or Numeric (for age) |
| **Outcome** | `prediction`, `label`, `outcome`, `target` | Binary (0/1) or Numeric Score |

**Sample Row:**
`{"age": 28, "gender": "Non-binary", "ethnicity": "Asian", "prediction": 1}`

---

## ⚖️ Legal Disclaimer

The Bias Auditor is intended for **internal fairness monitoring only**. While it uses industry-standard metrics like the 80% rule, a "Low Risk" result does not guarantee legal compliance, and a "High Risk" result does not definitively prove illegal discrimination. Always consult with legal and ethics experts when interpreting algorithmic fairness results.

---

## 👨‍💻 Author/Acknowledgements

>
>
> **Google Gemini** for this ReadMe
---
> **cswan300** — [GitHub Profile](https://github.com/cswan300)
