# Problem Statement & Project Charter

## 1. Executive Summary & Healthcare Context
Modern hospital networks operate under stringent operational, clinical, and financial constraints. Hospital administrators, clinical directors, and operations managers must balance bed occupancy, resource allocation, and payer reimbursement while maintaining quality of care and minimizing avoidable repeat visits. 

Without clean, systematic visibility into historical admission patterns, patient length of stay (LOS), diagnostic distributions, and billing variability, healthcare executives face significant challenges in capacity planning, cost containment, and operational benchmarking.

This project delivers a robust descriptive and diagnostic analytics framework alongside an executive Power BI dashboard using synthetic patient admission records. It provides healthcare leaders with objective, data-driven insights into patient throughput, cost drivers, readmission frequency, and provider-level operational metrics.

---

## 2. Core Business & Analytical Objectives
The project is organized around eight specific, actionable objectives:

1. **Admission, Discharge, and Patient Volume Trends**:
   * Measure temporal admission volume across months and years.
   * Evaluate seasonal variations, admission day-of-week patterns, and inpatient census dynamics.
2. **Patient Demographics Profiling**:
   * Quantify patient population distribution across standardized age brackets (`0-17`, `18-34`, `35-49`, `50-64`, `65+`), gender, and blood types.
   * Assess demographic mix across admission types (Emergency, Urgent, Elective).
3. **Common Diagnoses & Clinical Groupings**:
   * Profile primary medical conditions (e.g., Asthma, Cancer, Diabetes, Hypertension, Arthritis, Obesity).
   * Cross-tabulate prescribed medications and test result outcomes (`Normal`, `Abnormal`, `Inconclusive`) to evaluate clinical presentation profiles.
4. **Average Length of Stay (ALOS) Analysis**:
   * Compute mean ALOS alongside median LOS to account for right-skewed hospital stays.
   * Identify extended stays via `long_stay_flag` (defined as $\ge 90\text{th}$ percentile of `los_days`) across conditions and admission types.
5. **Billing and Insurance Utilization Patterns**:
   * Evaluate billing amount distributions per admission, per unique patient, and per inpatient day (`cost_per_day`).
   * Identify financial outliers via `high_cost_flag` (defined as $\ge 95\text{th}$ percentile of `billing_amount`) across insurance providers.
6. **30-Day Readmission Patterns (Derived Proxy)**:
   * Calculate 30-day readmissions based on subsequent admissions for the same anonymized patient (`days_to_next_admission` between 0 and 30 days).
   * Restrict calculations to `readmission_eligible` records where the discharge date is at least 30 days prior to the dataset end date.
   * Benchmark readmission rates across medical conditions and demographic groups.
7. **Comparative Performance Benchmarking**:
   * Compare operational metrics (ALOS, volume, billing) across facilities (`hospital`), pseudonymous physicians (`doctor_id`), and time periods.
   * Strictly apply sample size guardrails ($n \ge 30$) to prevent spurious conclusions on small cohorts.
8. **Interactive Power BI Executive Dashboard**:
   * Deliver an intuitive, multi-page business intelligence dashboard featuring:
     * **Page 1: Executive Overview** (KPI cards, volume trends, top medical conditions).
     * **Page 2: Demographic Profile** (age group distributions, gender splits, admission types).
     * **Page 3: Diagnosis & Clinical Patterns** (condition-medication matrices, test result outcomes).
     * **Page 4: Cost, Financials & Readmission** (billing analysis, insurer distribution, 30-day readmission proxy).

---

## 3. Scope Boundaries: In-Scope vs. Out-of-Scope

### In-Scope
* **Analytics Category**: Strictly **Descriptive and Diagnostic Analytics**.
* **Data Hygiene & Transformation**: Data cleaning, deduplication, date normalization, standardization, and canonical feature engineering (`los_days`, `patient_key`, `doctor_id`, `admission_id`, `cost_per_day`, flags).
* **Statistical Rigor**: Two-sample and multi-sample hypothesis testing (e.g., Mann-Whitney U, Kruskal-Wallis, Chi-square tests of independence) with normality checks, alpha ($\alpha = 0.05$), multiple comparison corrections, effect sizes, and non-causal interpretations.
* **Privacy & De-identification**: Salted SHA-256 pseudonymization of patient identifiers, pseudonymous doctor mapping, and complete elimination of direct personal identifiers.
* **Reporting & Dashboards**: Markdown technical documentation, automated privacy scans, Jupyter notebooks, structured CSV tables, figures, and interactive Power BI reporting.

### Out-of-Scope
* **No Predictive Modeling / Machine Learning**: No regression, classification, clustering, or deep learning algorithms (e.g., no readmission prediction models, no patient stay forecasting).
* **No Causal or Medical Determinations**: Statistical findings will reflect observational associations, not clinical causality or treatment efficacy.
* **No Data Fabrication**: Absent clinical attributes (e.g., clinical department, geographic address, procedure codes, patient satisfaction scores, discharge disposition) are documented as unavailable and never fabricated or simulated.

---

## 4. Target Users & Stakeholders
* **Hospital Chief Executive Officers (CEOs) & Chief Operating Officers (COOs)**: Seeking high-level operational visibility into facility throughput, bed utilization, and patient volume.
* **Chief Medical Officers (CMOs) & Clinical Governance Committees**: Monitoring condition distributions, test outcome anomalies, and readmission patterns.
* **Healthcare Financial Officers & Billing Directors**: Evaluating billing variations across commercial and government insurance providers and identifying high-cost outlier stays.
* **Hospital Quality & Capacity Managers**: Analyzing ALOS, weekend discharge bottlenecks, and room-level utilization.

---

## 5. Success Criteria
1. **Zero Privacy Violations**: 100% pass rate on automated privacy scan (`privacy_scan.py`), confirming no real patient names or physician names exist in downstream code, docs, tables, or figures.
2. **Data Consistency & Transparency**: Strict conformance to canonical schema names and definitions across all project phases.
3. **Reproducibility**: Notebooks and scripts run top-to-bottom without manual intervention, using relative paths and fixed random seeds (`seed = 42`).
4. **Statistical Validity**: Every statistical hypothesis test includes clear hypotheses ($H_0$, $H_1$), validated assumptions, test statistic, p-value, effect size, and a plain-English interpretation.
5. **Dashboard Usability**: An interactive, well-structured Power BI dashboard providing dynamic cross-filtering and drill-through capabilities across all four core analytical domains.

