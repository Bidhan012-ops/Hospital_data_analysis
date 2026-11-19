# Field Availability & Analytical Mapping Matrix

## 1. Overview and Structural Principles
This document maps each of the **8 core analytical objectives** and the **4 Power BI dashboard pages** to the available source and canonical columns, explicitly documents **missing clinical and operational fields**, and specifies the **methodological handling decisions** applied throughout this project.

### Core Non-Negotiable Decisions
1. **Clinical Department & Patient Location**:
   * **Source Reality**: The raw dataset does not record patient residential location, geographic jurisdiction, or hospital clinical department (e.g., Cardiology, Orthopedics, Oncology).
   * **Handling Strategy**: `medical_condition`, `hospital`, and `doctor_id` serve as the primary clinical and operational grouping axes. 
   * **Specialty Grouping Constraint**: If any clinical specialty or department mapping is referenced in reporting, it must follow an explicit, transparent lookup table clearly labelled as an **analytical assumption**, never misrepresented as native source data.
2. **Readmission Flag**:
   * **Source Reality**: No native readmission flag exists.
   * **Handling Strategy**: Readmission is derived strictly using the **30-day readmission proxy** defined in the project charter:
     $$\text{days\_to\_next\_admission} = \text{admission\_date}_{t+1} - \text{discharge\_date}_t$$
     $$\text{readmitted\_30d} = 1 \iff 0 \le \text{days\_to\_next\_admission} \le 30$$
     $$\text{readmission\_eligible} = 1 \iff \text{discharge\_date} + 30\text{ days} \le \max(\text{admission\_date})$$
     $$\text{Readmission Rate} = \frac{\sum \text{readmitted\_30d}}{\sum \text{readmission\_eligible}} \quad (\text{restricted to eligible index stays})$$
     This metric is explicitly labelled as **Derived 30-day Proxy**.
3. **Billing vs. Collections**:
   * **Source Reality**: Payment status (paid, pending, denied) is unavailable.
   * **Handling Strategy**: Financial analyses evaluate total and daily billed amounts (`billing_amount`, `cost_per_day`), explicitly stating that figures represent gross charges rather than net collections.

---

## 2. Objective-to-Field Mapping Matrix

| Objective # | Objective Title | Required Fields / Metrics | Source & Canonical Fields Used | Missing / Unavailable Fields | Handling & Analytical Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Obj 1** | **Admission, Discharge & Visit Trends** | Admission date, discharge date, volume over time, seasonality, census | `admission_id`, `admission_date`, `discharge_date`, `admission_month`, `admission_type` | Exact admission/discharge time (hours/minutes), bed occupancy status | Temporal aggregation conducted at daily, monthly (`YYYY-MM`), and annual grains. Same-day stays counted as 0 days. |
| **Obj 2** | **Demographics Profiling** | Age, age groupings, gender, blood type, admission acuity | `patient_key`, `age`, `age_group`, `gender`, `blood_type`, `admission_type` | Patient address, postal code, ethnicity, race, socioeconomic status | Demographic analysis performed across canonical `age_group` brackets (`0-17`, `18-34`, `35-49`, `50-64`, `65+`), gender, and blood type. |
| **Obj 3** | **Common Diagnoses & Groupings** | Medical condition, medication, test outcome distributions | `medical_condition`, `medication`, `test_results`, `admission_type` | ICD-10 diagnosis codes, CPT procedure codes, clinical stage/severity | Analyses group by primary `medical_condition`. Medication frequencies and test outcomes (`Normal`, `Abnormal`, `Inconclusive`) cross-tabulated directly. |
| **Obj 4** | **Average Length of Stay (ALOS)** | Stay duration in whole days, ALOS, median LOS, extended stay flag | `admission_id`, `los_days`, `admission_type`, `medical_condition`, `long_stay_flag` | Hourly timestamps, ICU stay hours, discharge disposition (home, hospice) | $\text{los\_days} = \text{discharge\_date} - \text{admission\_date}$. Both mean (ALOS) and median are reported. Outlier stays flagged via `long_stay_flag` ($\ge 90\text{th}$ percentile). |
| **Obj 5** | **Billing & Insurance Patterns** | Total charges, daily charges, payer breakdown, financial outliers | `billing_amount`, `cost_per_day`, `insurance_provider`, `high_cost_flag`, `patient_key` | Payment status (paid/denied), insurance claim approval, copay/deductible | Compute cost per admission (`billing_amount`), cost per patient, and $\text{cost\_per\_day} = \frac{\text{billing\_amount}}{\max(\text{los\_days}, 1)}$. Outliers flagged via `high_cost_flag` ($\ge 95\text{th}$ percentile). |
| **Obj 6** | **30-Day Readmission Patterns** | Prior/subsequent admissions, return intervals, readmission rate | `patient_key`, `admission_date`, `discharge_date`, `days_to_next_admission`, `readmitted_30d`, `readmission_eligible` | Native hospital readmission flag, planned vs. unplanned readmission reason | Derived 30-day proxy calculated across chronologically sorted admissions per `patient_key`. Restricted to `readmission_eligible` admissions. |
| **Obj 7** | **Comparative Performance Across Hospitals/Doctors** | Facility volume, physician caseload, ALOS, billing variation | `hospital`, `doctor_id`, `los_days`, `billing_amount`, `medical_condition` | Physician specialty, hospital bed capacity, medical department, HCAHPS scores | Facility benchmarking uses `hospital`. Physician analysis uses pseudonymous `doctor_id`. Enforce strict sample threshold: $n \ge 30$ admissions. Cohorts with $n < 30$ flagged as small sample. |
| **Obj 8** | **Interactive Power BI Dashboard** | Dynamic filtering, KPI cards, visual cross-filtering | All canonical fields: `admission_id`, `patient_key`, `doctor_id`, `hospital`, `medical_condition`, `los_days`, etc. | Live database connection, real-time telemetry | Star-schema data model built on `data/processed/hospital_clean.csv` supporting 4 dedicated dashboards. |

---

## 3. Power BI Dashboard Page Mapping

| Dashboard Page | Target Audience & Focus | Core Visuals & KPI Cards | Supporting Canonical Fields | Unavailable Data & Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Page 1: Executive Overview** | C-Suite / Executive Leadership: Total volume, bed utilization, revenue | - Total Admissions & Total Unique Patients<br>- Total Gross Billed & Overall ALOS (Mean/Median)<br>- Monthly Admission Volume Trend<br>- Admissions by Admission Type & Condition | `admission_id`, `patient_key`, `billing_amount`, `los_days`, `admission_month`, `admission_type`, `medical_condition` | No real-time bed census; uses historical monthly and daily admission volumes. |
| **Page 2: Demographic Profile** | Clinical Governance & Operations: Patient population mix | - Age Pyramid / Distribution by `age_group`<br>- Gender & Blood Type Breakdown<br>- Admission Type by Age Group<br>- Mean/Median ALOS by Demographic Segment | `age`, `age_group`, `gender`, `blood_type`, `admission_type`, `los_days` | No geographic or socio-demographic indicators; population profile bounded by age, gender, and blood type. |
| **Page 3: Diagnosis & Department** | Clinical Directors & Pharmacy: Clinical condition & diagnostic throughput | - Admissions by `medical_condition`<br>- Condition vs. `medication` Heatmap<br>- Test Result Breakdown (`Normal`, `Abnormal`, `Inconclusive`)<br>- Clinical Specialty Grouping (Explicit Lookup) | `medical_condition`, `medication`, `test_results`, `hospital`, `doctor_id`, `admission_id` | Native medical department is unavailable. Grouping relies on `medical_condition`. Any clinical department grouping is an explicit lookup table labelled as an assumption. |
| **Page 4: Cost & Readmission** | CFO, Finance, Quality Assurance: Financial risk and repeat hospitalizations | - Total & Average Billing by `insurance_provider`<br>- Daily Cost (`cost_per_day`) Distribution<br>- High-Cost Flag Outliers ($\ge 95\text{th}$ percentile)<br>- Derived 30-Day Readmission Rate by Condition | `billing_amount`, `cost_per_day`, `insurance_provider`, `high_cost_flag`, `readmitted_30d`, `readmission_eligible`, `medical_condition` | Readmission is a derived proxy, not native clinical adjudication. Payment realization/denials unavailable; gross billing analyzed. |

---

## 4. Explicit Lookup Table: Clinical Specialty Mapping Assumption
Because `medical_department` is absent from the source data, the following reference table represents the standard clinical grouping assumption when a department-level roll-up is required for administrative reporting:

| Medical Condition (`medical_condition`) | Derived Specialty Group (Analytical Assumption) | Rationale / Standard Clinical Alignment |
| :--- | :--- | :--- |
| **Asthma** | Pulmonology / Respiratory Medicine | Chronic inflammatory airway disorder managed under pulmonary care. |
| **Cancer** | Oncology | Neoplastic disease management and medical oncology care. |
| **Diabetes** | Endocrinology & Metabolic Disorders | Endocrine disorder requiring glycemic control and metabolic management. |
| **Hypertension** | Cardiology / Vascular Medicine | Primary cardiovascular and systemic circulatory management. |
| **Arthritis** | Rheumatology / Orthopedics | Joint inflammation and musculoskeletal disease management. |
| **Obesity** | Bariatrics / Preventive Medicine | Metabolic, lifestyle, and specialized weight management medicine. |

> **Audit Note**: This lookup table must be cited in all documentation and dashboard footnotes as an **analyst assumption**, not raw observational source data.
