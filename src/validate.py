"""
Validation Assertions Script (src/validate.py)
----------------------------------------------
Validates data integrity, chronological logic, categorical domains,
key uniqueness, and privacy compliance on data/processed/hospital_clean.csv.
Outputs results to outputs/tables/validation_report.csv.
"""

import sys
import pandas as pd
from pathlib import Path


def validate_clean_dataset(clean_df_path: str = "data/processed/hospital_clean.csv",
                           raw_df_path: str = "data/raw/healthcare_dataset.csv") -> pd.DataFrame:
    df_clean = pd.read_csv(clean_df_path)
    df_raw = pd.read_csv(raw_df_path)

    total_records = len(df_clean)
    raw_records = len(df_raw)

    validation_results = []

    def log_assertion(name: str, condition: str, violations: int, details: str = ""):
        passed = violations == 0
        validation_results.append({
            "assertion_name": name,
            "condition_checked": condition,
            "records_tested": total_records,
            "violations_count": violations,
            "status": "PASS" if passed else "FAIL",
            "details": details or ("All records satisfy assertion." if passed else f"Found {violations} violations.")
        })

    # 1. Nulls in key fields
    key_fields = ["admission_id", "patient_key", "doctor_id", "admission_date", 
                  "discharge_date", "los_days", "billing_amount", "medical_condition"]
    null_violations = int(df_clean[key_fields].isnull().sum().sum())
    log_assertion("no_nulls_in_key_fields", "key_fields.isnull().sum() == 0", null_violations)

    # 2. Chronological stay integrity
    adm_dt = pd.to_datetime(df_clean["admission_date"])
    dis_dt = pd.to_datetime(df_clean["discharge_date"])
    chrono_violations = int((dis_dt < adm_dt).sum())
    log_assertion("chronological_order", "discharge_date >= admission_date", chrono_violations)

    # 3. Non-negative LOS
    los_violations = int((df_clean["los_days"] < 0).sum())
    log_assertion("non_negative_los", "los_days >= 0", los_violations)

    # 4. Admission ID uniqueness
    id_dups = int(df_clean["admission_id"].duplicated().sum())
    log_assertion("admission_id_uniqueness", "admission_id.nunique() == len(df)", id_dups)

    # 5. Expected Categorical Sets
    valid_gender = {"Male", "Female"}
    gender_violations = int((~df_clean["gender"].isin(valid_gender)).sum())
    log_assertion("gender_categories", "gender in {'Male', 'Female'}", gender_violations)

    valid_blood = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    blood_violations = int((~df_clean["blood_type"].isin(valid_blood)).sum())
    log_assertion("blood_type_categories", "blood_type in valid 8 ABO/Rh types", blood_violations)

    valid_conditions = {"Cancer", "Diabetes", "Asthma", "Obesity", "Arthritis", "Hypertension"}
    condition_violations = int((~df_clean["medical_condition"].isin(valid_conditions)).sum())
    log_assertion("medical_condition_categories", "medical_condition in 6 primary conditions", condition_violations)

    valid_insurers = {"Medicare", "UnitedHealthcare", "Aetna", "Blue Cross", "Cigna"}
    insurer_violations = int((~df_clean["insurance_provider"].isin(valid_insurers)).sum())
    log_assertion("insurance_provider_categories", "insurance_provider in 5 major payers", insurer_violations)

    valid_adm_types = {"Emergency", "Urgent", "Elective"}
    adm_type_violations = int((~df_clean["admission_type"].isin(valid_adm_types)).sum())
    log_assertion("admission_type_categories", "admission_type in {'Emergency', 'Urgent', 'Elective'}", adm_type_violations)

    valid_meds = {"Paracetamol", "Ibuprofen", "Aspirin", "Penicillin", "Lipitor"}
    med_violations = int((~df_clean["medication"].isin(valid_meds)).sum())
    log_assertion("medication_categories", "medication in 5 approved pharmaceuticals", med_violations)

    valid_tests = {"Normal", "Abnormal", "Inconclusive"}
    test_violations = int((~df_clean["test_results"].isin(valid_tests)).sum())
    log_assertion("test_results_categories", "test_results in {'Normal', 'Abnormal', 'Inconclusive'}", test_violations)

    valid_age_groups = {"0-17", "18-34", "35-49", "50-64", "65+"}
    age_group_violations = int((~df_clean["age_group"].isin(valid_age_groups)).sum())
    log_assertion("age_group_categories", "age_group in 5 standard demographic tiers", age_group_violations)

    # 6. Age plausibility
    age_violations = int(((df_clean["age"] < 0) | (df_clean["age"] > 120)).sum())
    log_assertion("age_range_plausibility", "0 <= age <= 120", age_violations)

    # 7. Privacy: direct identifiers absent
    direct_id_present = ("Name" in df_clean.columns) or ("Doctor" in df_clean.columns)
    log_assertion("no_direct_identifiers", "'Name' and 'Doctor' dropped permanently", 1 if direct_id_present else 0)

    # 8. Row count reconciliation
    exact_raw_dups = int(df_raw.duplicated().sum())
    reconciled = (raw_records - exact_raw_dups) == total_records
    log_assertion("row_count_reconciliation", "raw_rows - exact_dupes == clean_rows", 0 if reconciled else 1,
                  details=f"Raw: {raw_records:,} - Dupes: {exact_raw_dups:,} = Clean: {total_records:,}")

    report_df = pd.DataFrame(validation_results)

    # Save to outputs/tables
    out_path = Path("outputs/tables/validation_report.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(out_path, index=False)
    print(f"Validation report saved to {out_path}")

    # Mirror to phase2_preprocessing
    p2_out = Path("phase2_preprocessing/validation_report.csv")
    p2_out.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(p2_out, index=False)
    print(f"Mirrored validation report to {p2_out}")

    print("\n" + "=" * 80)
    print("DATA PREPROCESSING VALIDATION REPORT SUMMARY")
    print("=" * 80)
    print(report_df.to_string(index=False))
    print("=" * 80)

    all_passed = (report_df["status"] == "PASS").all()
    if all_passed:
        print("[SUCCESS] All 15 validation assertions PASSED perfectly!")
    else:
        print("[FAILURE] Some validation assertions failed.")

    return report_df


if __name__ == "__main__":
    report = validate_clean_dataset()
    all_pass = (report["status"] == "PASS").all()
    sys.exit(0 if all_pass else 1)

