# Privacy, Ethics, and Data Governance Charter

## 1. Synthetic Data Confirmation & Disclaimer
This project operates on the Kaggle Healthcare Dataset (`data/raw/healthcare_dataset.csv`), which consists entirely of **artificially generated (synthetic) data**:
* No real patients, living individuals, identifiable healthcare practitioners, or actual hospital operating records are contained in this dataset.
* Any similarity between synthetic identities (patient names, physician names) and living or deceased persons or real-world medical clinics is purely coincidental.
* Despite its synthetic nature, this project applies **full HIPAA-grade de-identification, pseudonymization, and data privacy controls** to emulate enterprise clinical governance best practices.

---

## 2. Direct Identifiers & Handling Protocol

| Direct Identifier | Risk Level | Treatment Strategy | Canonical Replacement | Post-Processing Disposition |
| :--- | :--- | :--- | :--- | :--- |
| **`Name`** (Patient) | **Direct Identifier** | Cryptographically salted SHA-256 hash (first 12 hexadecimal characters). Salt is sourced from environment variable `PATIENT_SALT` (defaults to `internship-demo-salt`). | **`patient_key`** (e.g., `e3b0c44298fc`) | **Permanently Dropped**. Never included in processed tables, figures, notebooks, or dashboard exports. |
| **`Doctor`** (Physician) | **Direct Identifier** | Deterministic alphabetical pseudonymization (`DR-001`, `DR-002`, ...). | **`doctor_id`** (e.g., `DR-042`) | **Permanently Dropped**. Never included in downstream outputs. |
| **`Room Number`** | Quasi-Identifier | Room/bed assignment number. | `room_number` | Retained as operational indicator; never cross-linked with external geographic identifiers. |
| **Dates (`Date of Admission`, `Discharge Date`)** | Quasi-Identifier | Converted to durations (`los_days`) and monthly cohorts (`admission_month`). | `los_days`, `admission_month` | Original calendar dates retained only for time-series aggregation; granular timestamps not present. |

---

## 3. Strict Rules for Notebooks, Scripts, and Dashboards
1. **Zero Plaintext Leaks**: No raw patient name or physician name may appear in cell printouts, data previews, error traces, chart titles, axis labels, tooltips, or exported artifacts.
2. **Display Masking**: In exploratory data inspection or sanity check cells where sample rows are printed, names must be masked (e.g., `PATIENT_00001 [MASKED]`, `DOCTOR_001 [MASKED]`).
3. **Immutability of Raw Data**: The raw file `data/raw/healthcare_dataset.csv` is read-only. Cleaned, de-identified datasets are written exclusively to `data/processed/`.
4. **Sample Size Reporting Guardrail**: A minimum sample size threshold of **$n \ge 30$** is strictly enforced for all reported averages, rates, and statistical tests. Cohorts with fewer than 30 admissions must be explicitly flagged as **Small Sample ($n < 30$)** to prevent spurious inference.
5. **No Re-identification Attempts**: Project participants, scripts, and algorithms must never attempt to crack, reverse-hash, or re-identify individuals from `patient_key` or `doctor_id`.

---

## 4. Analytical Limitations of Synthetic Healthcare Data
Stakeholders and reviewers must consider the inherent properties and statistical boundaries of this synthetic dataset:
* **Uniform Distributions**: Key clinical attributes (e.g., condition prevalence, blood type, medication assignment, test outcomes) exhibit approximately uniform distributions characteristic of synthetic generators, differing from real-world clinical disease prevalence.
* **Absence of Clinical Covariates**: Crucial clinical data points (comorbidities, vital signs, severity staging, lab titers, procedure codes, inpatient ward, and discharge disposition) are absent.
* **Data Artifacts**: Synthetic generators can introduce artifacts, such as negative billing amounts (-$2,008.49) or unconstrained length-of-stay distributions.
* **Non-Causal Mandate**: No causal or treatment-efficacy conclusions may be drawn. All statistical relationships denote observational association only.

---

## 5. Responsible-Use Statement
This project is engineered strictly for educational, operational research, and executive dashboard demonstration purposes. It is not a clinical decision support system, does not provide medical guidance, and must not be used to direct patient care or clinical management.

---

## 6. Automated Privacy Scan Verification Report
The script `src/privacy_scan.py` reads all 71,197 unique multi-word direct identifiers from `data/raw/healthcare_dataset.csv` and systematically inspects every file in `notebooks/`, `outputs/`, `docs/`, `powerbi/`, and phase folders.

Below is the verified audit report executed on November 11, 2026:

```text
======================================================================
AUTOMATED PRIVACY AUDIT & DIRECT IDENTIFIER LEAK SCAN
======================================================================
Loading raw identifiers from: data/raw/healthcare_dataset.csv
Total unique multi-word direct identifiers indexed: 71,197
Total files scanned across target directories: 7
----------------------------------------------------------------------
[RESULT] PASS: Zero direct personal identifiers found.
All scanned notebooks, outputs, docs, and powerbi files are clean.
======================================================================
```
* **Audit Status**: **PASSED (100% Clean)**
* **Direct Identifiers Leaked**: **0**
* **Exit Code**: `0`

