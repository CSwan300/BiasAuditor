# Frontend Test Case Register

This document tracks all test cases for the React-based frontend of the BiasAuditor platform.

## Test Case Grid

| ID     | Component / Module | Test Type   | Purpose                                                 | Input / Condition                                         | Expected Result                                                           |
|--------|--------------------|-------------|---------------------------------------------------------|-----------------------------------------------------------|---------------------------------------------------------------------------|
| APP-01 | App.tsx            | Smoke       | Verify main layout and branding are loaded.             | Initial Render.                                           | "BiasAuditor" header and "Algorithmic Fairness" text are visible.         |
| HDR-01 | Header.tsx         | Unit        | Ensure branding is present and correct.                 | Render `<Header />`.                                      | Displays "Bias" and "Auditor" with correct styling.                       |
| HDR-02 | Header.tsx         | Theme       | Verify default theme initialization.                    | Initial Render.                                           | `data-theme="dark"` is set on the root element.                           |
| HDR-03 | Header.tsx         | Persistence | Verify theme toggle updates storage.                    | Click "Light Mode".                                       | `localStorage` saves "light" and document attribute updates instantly.    |
| HER-01 | Hero.tsx           | Content     | Verify educational terminology is visible.              | Render `<Hero />`.                                        | Contains references to "Four-Fifths Rule" and "Statistical Significance". |
| HER-02 | Hero.tsx           | Visual      | Ensure feature pills render correctly.                  | Render `<Hero />`.                                        | Exactly 4 feature pills (Intersectionality, etc.) are present.            |
| CFG-01 | AuditConfig.tsx    | Validation  | Prevent premature audit execution.                      | No file selected.                                         | "Run Audit" button is disabled.                                           |
| CFG-02 | AuditConfig.tsx    | Interaction | Verify file selection enables UI.                       | Upload `dataset.csv`.                                     | Filename is displayed; "Run Audit" button becomes enabled.                |
| CFG-03 | AuditConfig.tsx    | Logic       | Ensure data is passed correctly to parent.              | 80% Threshold + "hired" column.                           | `onRun` called with `(file, 0.8, 'hired')`.                               |
| CFG-04 | AuditConfig.tsx    | Robustness  | Prevent unsupported file uploads.                       | Drop `image.png`.                                         | `window.alert` triggered; file is rejected.                               |
| BNR-01 | RiskBanner.tsx     | State       | Verify styling changes based on risk.level: 'Critical'. | Banner applies `.critical` class (Red border/background). |                                                                           |
| BNR-02 | RiskBanner.tsx     | Visual      | Verify math explanation rendering.                      | Render `<RiskBanner />`.                                  | 100/80/0% breakdown text is visible with correct line breaks.             |
| CRD-01 | AuditCard.tsx      | Unit        | Verify attribute flagging visualization.                | `flag: true`.                                             | "Flagged" badge appears; bar fill color changes to Red.                   |
| CRD-02 | AuditCard.tsx      | Data        | Ensure selection rates match audit data.                | Group A: 80%.                                             | Bar width and text label reflect 80% selection rate.                      |
| RES-01 | AuditResults.tsx   | Integration | Verify dashboard structure.                             | Valid Audit Object.                                       | Displays Banner, Audit Cards, and Mitigation cards simultaneously.        |
| RES-02 | AuditResults.tsx   | Interaction | Verify "New Audit" resets view.                         | Click "New Audit".                                        | `onReset` callback is executed.                                           |
| RES-03 | AuditResults.tsx   | Async/API   | Verify PDF download functionality.                      | Click "Download PDF".                                     | `fetch` called for `/report/pdf`; Browser receives and processes Blob.    |
| RES-04 | AuditResults.tsx   | Error       | Handle backend PDF generation failure.                  | Backend returns 500.                                      | UI shows alert: "PDF generation failed".                                  |
| FTR-01 | Footer.tsx         | Unit        | Verify legal/project disclaimer.                        | Render `<Footer />`.                                      | Displays "Open Source Algorithmic Fairness Audit Tool".                   |

## Implementation Summary

These tests are designed to be executed using Vitest and React Testing Library.

- Unit tests (HDR, HER, FTR, BNR): Focus on rendering logic and static content.
- Integration tests (CFG, RES): Focus on how components communicate and interact with the backend API.
- State tests (HDR, CFG): Ensure user choices like theme and thresholds persist or are converted correctly before audit logic.