# Data Dictionary & Variable Specifications

This document defines the technical schema, data types, privacy classifications, operational ranges, and mathematical derivation rules for all **raw source fields** and **canonical derived features** utilized across the Hospital Patient Data Analysis project.

---

## 1. Raw Source Columns

| Column Name | Data Type | Allowed Values / Empirical Range | Privacy Classification | Used in Analysis? | Description |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **`Name`** | String (Text) | Free-text personal full name | **Direct Identifier** | **No** (Dropped) | Patient full name. Masked in all displays and dropped immediately upon computing `patient_key`. |
| **`Age`** | Integer | 13 to 89 | Quasi-Identifier | **Yes** | Patient chronological age in whole years at admission intake. Renamed to canonical `age`. |
| **`Gender`** | String | `'Male'`, `'Female'` | Quasi-Identifier | **Yes** | Biological sex / reported gender of the admitted patient. Standardized and renamed to canonical `gender`. |
| **`Blood Type`** | String | `'A+'`, `'A-'`, `'B+'`, `'B-'`, `'AB+'`, `'AB-'`, `'O+'`, `'O-'` | Non-Identifying | **Yes** | ABO and Rhesus blood classification. Renamed to canonical `blood_type`. |
| **`Medical Condition`** | String | `'Cancer'`, `'Diabetes'`, `'Asthma'`, `'Obesity'`, `'Arthritis'`, `'Hypertension'` | Non-Identifying | **Yes** | Primary diagnosed clinical condition for admission. Renamed to canonical `medical_condition`. |
| **`Date of Admission`** | Date / String | `YYYY-MM-DD` (2019-05-08 to 2024-05-07) | Quasi-Identifier | **Yes** | Formal hospital admission date. Converted to datetime and renamed to canonical `admission_date`. |
| **`Doctor`** | String (Text) | Free-text physician name | **Direct Identifier** | **No** (Dropped) | Attending physician name. Masked in all displays and dropped immediately upon computing `doctor_id`. |
| **`Hospital`** | String | Multi-facility institution name | Non-Identifying | **Yes** | Name of the admitting medical facility. Renamed to canonical `hospital`. |
| **`Insurance Provider`** | String | `'Medicare'`, `'UnitedHealthcare'`, `'Aetna'`, `'Blue Cross'`, `'Cigna'` | Non-Identifying | **Yes** | Payer organization responsible for primary coverage. Renamed to canonical `insurance_provider`. |
| **`Billing Amount`** | Float | Numeric currency ($1,000 to $60,000+) | Non-Identifying | **Yes** | Total gross charges billed for the admission episode. Renamed to canonical `billing_amount`. |
| **`Room Number`** | Integer | Numeric room/bed number (101 to 500) | Quasi-Identifier | **Yes** | Assigned inpatient room or bed number. Renamed to canonical `room_number`. |
| **`Admission Type`** | String | `'Emergency'`, `'Urgent'`, `'Elective'` | Non-Identifying | **Yes** | Clinical intake acuity. Renamed to canonical `admission_type`. |
| **`Discharge Date`** | Date / String | `YYYY-MM-DD` (2019-05-09 to 2024-06-06) | Quasi-Identifier | **Yes** | Inpatient discharge date. Converted to datetime and renamed to canonical `discharge_date`. |
| **`Medication`** | String | `'Paracetamol'`, `'Ibuprofen'`, `'Aspirin'`, `'Penicillin'`, `'Lipitor'` | Non-Identifying | **Yes** | Primary therapeutic medication prescribed. Renamed to canonical `medication`. |
| **`Test Results`** | String | `'Normal'`, `'Abnormal'`, `'Inconclusive'` | Non-Identifying | **Yes** | Diagnostic test outcome classification. Renamed to canonical `test_results`. |

---

## 2. Canonical Derived Columns

| Canonical Field | Data Type | Format / Allowed Values | Privacy Class | Exact Derivation Rule | Analytical Purpose & Definition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`admission_id`** | String | `'A'` + 6 digits (e.g., `A000001`, `A000042`) | Non-Identifying | `'A' + str(raw_row_index).zfill(6)` | Immutable, unique surrogate key identifying each admission record. |
| **`patient_key`** | String | 12 hex characters (e.g., `e3b0c44298fc`) | Pseudonym | `hashlib.sha256((PATIENT_SALT + Name.strip().upper()).encode('utf-8')).hexdigest()[:12]` | Cryptographically salted pseudonymous identifier enabling multi-visit tracking without exposing personal names. Salt defaults to `internship-demo-salt`. |
| **`age_group`** | String | `'0-17'`, `'18-34'`, `'35-49'`, `'50-64'`, `'65+'` | Non-Identifying | Discretized: <br>• `< 18` $\rightarrow$ `0-17`<br>• `18–34` $\rightarrow$ `18-34`<br>• `35–49` $\rightarrow$ `35-49`<br>• `50–64` $\rightarrow$ `50-64`<br>• $\ge 65$ $\rightarrow$ `65+` | Demographic age stratification standardizing cohort analysis across hospital departments. |
| **`los_days`** | Integer | Whole days $\ge 0$ | Non-Identifying | `(discharge_date - admission_date).days` | Length of hospital stay. Same-day admissions/discharges are recorded as 0 days. Mean represents ALOS. |
| **`admission_month`** | String | `'YYYY-MM'` (e.g., `2024-01`) | Non-Identifying | `admission_date.strftime('%Y-%m')` | Time-series monthly bucket for longitudinal volume and trend visualization. |
| **`doctor_id`** | String | `'DR-'` + 3 digits (e.g., `DR-001`) | Pseudonym | Deterministic alphabetical ordering of distinct Doctor names: `'DR-' + str(i + 1).zfill(3)` | Pseudonymous ID protecting physician privacy while allowing provider-level workload and performance benchmarking. |
| **`cost_per_day`** | Float | Billed currency per day | Non-Identifying | `billing_amount / max(los_days, 1)` | Average daily billed charge. Safeguards against division by zero for same-day stays ($\text{los\_days} = 0$). |
| **`high_cost_flag`** | Integer | `0` or `1` | Non-Identifying | `1 if billing_amount >= quantile(0.95) else 0` | Flags top 5% of expensive admissions for financial outlier review. |
| **`long_stay_flag`** | Integer | `0` or `1` | Non-Identifying | `1 if los_days >= quantile(0.90) else 0` | Flags top 10% of extended stays for capacity and utilization review. |
| **`days_to_next_admission`** | Float | Integer days or `NaN` | Non-Identifying | `next_admission_date - current_discharge_date` (per `patient_key` sorted by date) | Elapsed days until the patient's next admission episode. |
| **`readmitted_30d`** | Integer | `0` or `1` | Non-Identifying | `1 if 0 <= days_to_next_admission <= 30 else 0` | Binary 30-day readmission proxy indicating a repeat hospital stay within 30 days of discharge. |
| **`readmission_eligible`** | Integer | `0` or `1` | Non-Identifying | `1 if discharge_date + 30 days <= max(admission_date) else 0` | Right-censoring filter ensuring only patients with a full 30-day follow-up observation window are counted in the readmission rate denominator. |

---

## 3. Unavailable Fields (Documented as Absent)
In strict accordance with project rules, the following clinical and operational fields **do not exist** in the raw dataset and are **never fabricated**:
1. **Patient Location**: Street address, city, state, postal code.
2. **Medical Department**: Ward/specialty assignment (e.g., Cardiology, Oncology). Handled via `medical_condition` and explicit lookup assumptions.
3. **Native Readmission Flag**: No clinical indicator for unplanned readmissions. Handled via derived proxy.
4. **Payment Status**: Claim realization, copays, collections, bad debt.
5. **Procedure Details**: CPT/HCPCS codes, surgical interventions.
6. **Patient Satisfaction Scores**: HCAHPS surveys, patient feedback scores.
