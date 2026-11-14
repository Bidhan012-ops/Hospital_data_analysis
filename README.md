# Hospital Patient Data Analysis and Dashboard Development

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811.svg)](https://powerbi.microsoft.com/)
[![Privacy Audit](https://img.shields.io/badge/Privacy_Scan-PASSED-green.svg)](docs/privacy_and_ethics.md)
[![Analytics](https://img.shields.io/badge/Analytics-Descriptive%20%26%20Diagnostic-orange.svg)]()

> **Project Title**: Hospital Patient Data Analysis and Dashboard Development Using Python and Power BI  
> **Project Type**: B.Tech Internship, Intermediate Level, Healthcare Analytics  
> **Analytical Scope**: Descriptive and Diagnostic Analytics ONLY (No Machine Learning, No Predictive Models).  
> **Target Audience**: Hospital Administrators, Clinical Department Chairs, Operations Directors, and Healthcare Financial Executives.

---

## 1. Project Overview & Business Problem
Modern hospital systems operate under complex clinical, financial, and operational constraints. Inpatient facilities must balance bed occupancy, manage patient throughput, mitigate billing disparities across payers, and monitor avoidable readmissions—all while maintaining high-quality clinical care.

This project delivers an end-to-end healthcare analytics solution and an executive Power BI business intelligence suite using 55,500 patient admission records. The analytical pipeline translates raw clinical data into actionable administrative intelligence through rigorous data cleansing, cryptographic de-identification, exploratory data analysis, formal hypothesis testing, and interactive multi-page reporting.

### Core Objectives
1. **Admission, Discharge & Inpatient Volume Trends**: Temporal volume trends, monthly seasonality, and weekday intake patterns.
2. **Patient Demographics Profiling**: Age stratification (`0-17`, `18-34`, `35-49`, `50-64`, `65+`), gender parity, and blood types across admission urgency.
3. **Common Diagnoses & Clinical Groupings**: Primary condition prevalence, medication cross-tabulation, and diagnostic test outcome distributions.
4. **Average Length of Stay (ALOS)**: Mean (15.54 d) and median (16.00 d) LOS evaluation, identifying extended stays (`long_stay_flag` $\ge 90\text{th}$ percentile = 27 days).
5. **Billing and Insurance Utilization**: Total ($1.404B) and daily billed charges (`cost_per_day`), insurer breakdowns, and financial outliers (`high_cost_flag` $\ge 95\text{th}$ percentile = 47,638.27 CU).
6. **30-Day Readmission Patterns**: Derived proxy readmission tracking using sequential patient stays and censoring criteria (`readmission_eligible`).
7. **Comparative Performance Benchmarking**: Facility and pseudonymous physician (`doctor_id`) operational comparisons under minimum sample size guardrails ($n \ge 30$).
8. **Interactive Power BI Dashboard**: 4-page executive dashboard (Overview, Demographics, Diagnosis and Department, Cost and Readmission).

---

## 2. Project Repository Structure

```text
Hospital_data_analysis/
├── data/
│   ├── raw/                        # Immutable, read-only raw dataset (55,500 records)
│   │   └── healthcare_dataset.csv
│   └── processed/                  # Cleaned, anonymized canonical dataset (54,966 records)
│       └── hospital_clean.csv
├── notebooks/                      # Fully executed Jupyter notebooks (Phases 1-5)
│   ├── 01_data_inspection.ipynb   # Raw schema, cardinality & missingness audit
│   ├── 02_preprocessing.ipynb      # ETL cleaning, deduplication & canonical feature derivation
│   ├── 03_eda.ipynb                # Descriptive statistics, volume trends & demographic profiling
│   ├── 04_los_analysis.ipynb       # Length of stay distributions, bootstrapping & hypothesis tests
│   └── 05_cost_analysis.ipynb      # Financial analytics, payer breakdown & cost-LOS decoupling
├── src/                            # Modular, reproducible Python pipelines
│   ├── clean.py                    # Production ETL clean_dataset() pipeline
│   ├── validate.py                 # 15-point automated data quality assertion suite
│   ├── privacy_scan.py            # Automated direct identifier leak audit (71,197 names)
│   ├── eda_analysis.py             # Phase 3 automated EDA execution engine
│   ├── los_analysis.py             # Phase 4 automated LOS statistical suite
│   └── cost_analysis.py            # Phase 5 automated financial & payer statistical suite
├── docs/                           # Technical specifications and governance documentation
│   ├── problem_statement.md       # Problem charter, scope boundaries & 8 objectives
│   ├── data_dictionary.md         # Full data dictionary with privacy classes & formulas
│   ├── data_dictionary.csv        # Machine-readable schema dictionary
│   ├── field_availability_matrix.md# Analytical mapping & missing field handling
│   ├── preprocessing_report.md    # Deduplication, transformation & outlier log
│   ├── privacy_and_ethics.md      # Salted SHA-256 protocol & zero-leak audit results
│   └── source_attribution.md      # Data provenance and synthetic dataset attribution
├── outputs/
│   ├── figures/                   # 30+ publication-grade 150-DPI analytical figures
│   └── tables/                    # Reconciled summary CSVs, stat tests & key findings
├── powerbi/                        # Power BI dashboard templates (.pbix) and data model
├── .env.example                   # Environment variable template (PATIENT_SALT)
├── requirements.txt               # Pinned Python package dependencies
└── README.md                      # Project overview and navigation guide
```

---

## 3. Data Privacy & Canonical Standards

### De-identification Protocol
* **Patient Privacy**: Direct name is cryptographically hashed via salted SHA-256 into a 12-character pseudonym (`patient_key`). Salt is configurable via `PATIENT_SALT` (default: `internship-demo-salt`). `Name` is permanently eliminated.
* **Physician Privacy**: Attending doctor names are transformed into deterministic pseudonyms (`DR-001`, `DR-002`, ...) and dropped permanently.
* **Automated Audit**: `src/privacy_scan.py` scans all repository deliverables against 71,197 direct identifiers to guarantee zero privacy leakage.

### Canonical Derived Metrics
* **`los_days`**: `(discharge_date - admission_date).days` (Whole calendar days; same-day stays = 0).
* **`ALOS`**: Mean `los_days` (15.54 d), reported alongside median `los_days` (16.00 d).
* **`cost_per_day`**: `billing_amount / max(los_days, 1)` (Mean: 3,392.47 CU/d, Median: 1,649.59 CU/d).
* **`high_cost_flag`**: $\text{billing\_amount} \ge 95\text{th}\text{ percentile}$ (47,638.27 CU, 2,749 admissions).
* **`long_stay_flag`**: $\text{los\_days} \ge 90\text{th}\text{ percentile}$ (27 days, 5,531 admissions).
* **`readmitted_30d`**: Return visit for same `patient_key` with $0 \le \text{days\_to\_next\_admission} \le 30$.
* **`readmission_eligible`**: $\text{discharge\_date} + 30\text{ days} \le \max(\text{admission\_date})$.
* **Reporting Guardrail**: Minimum group size $n \ge 30$ for rates and statistical metrics.

---

## 4. Analytical Governance & Boundaries
* **Purely Descriptive & Diagnostic**: No predictive models, regression scoring, or machine learning algorithms are employed.
* **Non-Causal Language**: All empirical findings use associative terminology (*"is associated with"*, *"differs across"*); no clinical causal claims are made.
* **Missing Fields Documented**: Unrecorded fields (clinical department, patient address, procedure codes, native readmission, payment status, patient satisfaction) are explicitly recorded as absent and never fabricated.
