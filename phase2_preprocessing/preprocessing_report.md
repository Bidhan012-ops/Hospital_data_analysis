# Data Preprocessing & Canonical Feature Engineering Report

## 1. Executive Summary & Objective
This report documents the end-to-end data cleansing, de-identification, and canonical feature engineering pipeline implemented in **Phase 2: Data Preprocessing**. 

The goal of this phase is to turn the raw dataset (`data/raw/healthcare_dataset.csv`) into an analysis-ready canonical dataset (`data/processed/hospital_clean.csv`) with zero missing values, zero exact duplicates, no direct identifiers, verified chronological logic, and complete statistical auditability.

---

## 2. Before vs. After Cleansing Reconciliation Table

| Dimension / Metric | Before Cleansing (Raw Dataset) | After Cleansing (Canonical Dataset) | Net Delta / Transformation Rationale |
| :--- | :--- | :--- | :--- |
| **Total Rows (Admissions)** | 55,500 | 54,966 | **-534 rows** (Exact duplicate records purged; first occurrence kept). |
| **Exact Duplicate Rows** | 534 | 0 | 100% eliminated to prevent statistical inflation. |
| **Near-Duplicate Admissions** | 5,504 (Unflagged) | 5,466 (Flagged) | Flagged via `near_duplicate_flag = 1`; retained per non-silent-drop policy. |
| **Direct Patient Identifiers** | Present (`Name`) | **None** (Permanently Dropped) | Cryptographically transformed into 12-char salted SHA-256 `patient_key`. |
| **Direct Physician Identifiers** | Present (`Doctor`) | **None** (Permanently Dropped) | Deterministically mapped to pseudonymous `doctor_id` (`DR-001`...). |
| **Missing Values (Nulls)** | 0 (100% Complete) | 0 (100% Complete) | Source dataset exhibits full completeness; zero imputation required. |
| **Total Column Count** | 15 source columns | 32 canonical columns | **+17 feature columns** added (temporal, cost, flags, readmissions). |
| **Date Column Data Types** | `object` (string) | `datetime64[ns]` | Explicitly parsed using format `%Y-%m-%d`. |
| **Negative Billed Records** | 108 records (Unflagged) | 106 records (Flagged) | Flagged via `billing_outlier_flag = 1`; preserved per non-deletion policy. |
| **Stay Duration Range** | 1 to 30 days | 1 to 30 days (`los_days`) | Validated $\text{discharge\_date} \ge \text{admission\_date}$; zero inversions. |

### Row Count Reconciliation Proof
$$\text{Raw Rows } (55,500) - \text{Exact Duplicate Rows } (534) = \text{Clean Rows } (54,966)$$
$$\text{Reconciliation Discrepancy} = 0 \text{ rows}$$

---

## 3. Full Data Quality Decision Log

The following decision matrix records every audited issue, rows affected, cleansing action taken, and corresponding rationale:

| Issue Audited | Rows Affected | Action Taken | Methodological Rationale |
| :--- | :---: | :--- | :--- |
| **Missing / Null Values** | 0 | Retained (No imputation needed) | All 15 source columns are 100% populated with zero missing entries. |
| **Exact Duplicate Rows** | 534 | Dropped 534 duplicate records | Exact duplicate records artificially inflate hospital volume and distort clinical frequencies. First occurrence preserved; duplicates dropped. |
| **Near-Duplicate Records** | 5,466 | Flagged via `near_duplicate_flag = 1` | Records sharing identical `patient_key`, `admission_date`, and `medical_condition`. Retained per non-silent-drop rule as they may represent transfers or multi-test encounters. |
| **Direct Patient Identifier** | 55,500 | Salted SHA-256 hash (`patient_key`); `Name` dropped | Compliance with HIPAA Privacy Rule and non-negotiables. Salt defaults to `internship-demo-salt`. Direct names permanently purged. |
| **Direct Physician Identifier** | 55,500 | Mapped to `doctor_id` (`DR-001`...); `Doctor` dropped | Preserves provider-level operational tracking while completely eliminating physician names. |
| **Text Casing & Stray Spaces** | 55,500 | Trimmed whitespace and normalized strings | Standardizes categorical levels across facilities, payers, admission types, and medications. |
| **String Date Formats** | 55,500 | Parsed with format `YYYY-MM-DD` | Converted to native datetime objects. Verified zero chronological inversions (`discharge_date >= admission_date`). |
| **Implausible Age Values** | 0 | Validated (Retained all) | All patient ages fall between 13 and 89 years, strictly within the valid [0, 120] range. |
| **Negative Billing Amounts** | 106 | Flagged via `billing_outlier_flag = 1` | Synthetic generator artifact (minimum: -$2,008.49). Preserved with explicit flag per non-deletion outlier policy to maintain audit trail. |
| **Statistical Billing Outliers** | 106 | Evaluated using 1.5*IQR & 3-sigma | Due to uniform distribution up to $52,764, only negative values exceed bounds. Flagged via `billing_outlier_flag = 1`. |
| **Statistical LOS Outliers** | 0 | Evaluated using 1.5*IQR & 3-sigma | Length of stay is strictly bounded between 1 and 30 days; no records exceed statistical outlier bounds. Flagged via `los_outlier_flag = 0`. |
| **Missing Readmission Flag** | 54,966 | Engineered derived 30-day readmission proxy | Chronologically ordered admissions per patient; calculated `days_to_next_admission`, `readmitted_30d`, and `readmission_eligible`. |

---

## 4. Derived Canonical Features Specification

| Feature Name | Type | Formula / Logic | Clinical & Operational Purpose |
| :--- | :--- | :--- | :--- |
| **`admission_id`** | String | `'A' + str(raw_row_num).zfill(6)` | Immutable identifier preserving raw row reference. |
| **`patient_key`** | String | `sha256(salt + Name.upper())[:12]` | Salted pseudonymous patient surrogate key. |
| **`doctor_id`** | String | `DR-001`, `DR-002`, ... | Pseudonymous physician surrogate key. |
| **`los_days`** | Integer | `(discharge_date - admission_date).days` | Inpatient stay duration in whole days. |
| **`age_group`** | String | Discretized: `0-17`, `18-34`, `35-49`, `50-64`, `65+` | Standardized demographic age brackets. |
| **`admission_month`** | String | `admission_date.strftime('%Y-%m')` | Monthly cohort bucket for time-series trends. |
| **`admission_year`** | Integer | `admission_date.dt.year` | Calendar year of admission. |
| **`admission_quarter`** | String | `admission_date.dt.to_period('Q')` | Calendar quarter of admission (e.g., `2023Q1`). |
| **`admission_weekday`** | String | `admission_date.dt.day_name()` | Intake day of the week (e.g., `Monday`). |
| **`discharge_month`** | String | `discharge_date.dt.strftime('%Y-%m')` | Monthly cohort bucket for discharge throughput. |
| **`cost_per_day`** | Float | `billing_amount / max(los_days, 1)` | Average daily billed charges. |
| **`high_cost_flag`** | Integer | `1 if billing_amount >= p95 else 0` | Flags top 5% most expensive admissions ($\ge \$48,778.68$). |
| **`long_stay_flag`** | Integer | `1 if los_days >= p90 else 0` | Flags top 10% longest stays ($\ge 27\text{ days}$). |
| **`days_to_next_admission`** | Float | $\text{admission\_date}_{t+1} - \text{discharge\_date}_t$ | Elapsed days until next stay for the same patient. |
| **`readmitted_30d`** | Integer | `1 if 0 <= days_to_next_admission <= 30 else 0` | Derived 30-day readmission indicator. |
| **`readmission_eligible`** | Integer | `1 if discharge_date + 30d <= max(admission_date) else 0` | Right-censoring filter ensuring complete 30-day follow-up. |
| **`near_duplicate_flag`** | Integer | `1 if duplicated([patient_key, adm_date, condition]) else 0` | Flags potential duplicate or intra-day transfer visits. |
| **`billing_outlier_flag`** | Integer | `1 if outlier by IQR/z-score/negative else 0` | Identifies anomalous or negative billing entries. |
| **`los_outlier_flag`** | Integer | `1 if outlier by IQR/z-score else 0` | Identifies extreme length of stay outliers. |

---

## 5. Validation Assertions Report Summary
All 15 assertions implemented in `src/validate.py` were executed against `data/processed/hospital_clean.csv`. Every single assertion **PASSED** with zero violations:

```text
================================================================================
DATA PREPROCESSING VALIDATION REPORT SUMMARY
================================================================================
assertion_name                 condition_checked                               records_tested  violations  status
no_nulls_in_key_fields         key_fields.isnull().sum() == 0                           54966           0    PASS
chronological_order            discharge_date >= admission_date                         54966           0    PASS
non_negative_los               los_days >= 0                                            54966           0    PASS
admission_id_uniqueness        admission_id.nunique() == len(df)                        54966           0    PASS
gender_categories              gender in {'Male', 'Female'}                             54966           0    PASS
blood_type_categories          blood_type in valid 8 ABO/Rh types                       54966           0    PASS
medical_condition_categories   medical_condition in 6 primary conditions                54966           0    PASS
insurance_provider_categories  insurance_provider in 5 major payers                     54966           0    PASS
admission_type_categories      admission_type in {'Emergency', 'Urgent', 'Elective'}     54966           0    PASS
medication_categories          medication in 5 approved pharmaceuticals                 54966           0    PASS
test_results_categories        test_results in {'Normal', 'Abnormal', 'Inconclusive'}   54966           0    PASS
age_group_categories           age_group in 5 standard demographic tiers                54966           0    PASS
age_range_plausibility         0 <= age <= 120                                          54966           0    PASS
no_direct_identifiers          'Name' and 'Doctor' dropped permanently                  54966           0    PASS
row_count_reconciliation       raw_rows - exact_dupes == clean_rows                     54966           0    PASS
================================================================================
[SUCCESS] All 15 validation assertions PASSED perfectly!
```

---

## 6. Privacy Scan Verification
The automated privacy scanner (`src/privacy_scan.py`) was executed across all markdown reports, CSV tables, scripts, and notebook outputs.
* **Indexed Direct Identifiers**: 71,197 multi-word personal names and physician names.
* **Files Scanned**: 17 files across `notebooks/`, `docs/`, `outputs/`, `powerbi/`, and `phase2_preprocessing/`.
* **Violations Found**: **0 (Zero)**.
* **Status**: **PASSED (100% Clean)**.
