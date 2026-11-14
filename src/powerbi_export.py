"""
Power BI Star Schema Data Preparation and Export Script
Exports Fact and Dimension tables from data/processed/hospital_clean.csv into powerbi/
Applies sample size guardrail (n >= 30) for hospital facilities to eliminate spurious small-sample
variations and synthetic name collisions.
"""

import os
import pandas as pd
import numpy as np

def export_powerbi_star_schema():
    input_path = os.path.join("data", "processed", "hospital_clean.csv")
    output_dir = "powerbi"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading processed data from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} admissions records.")
    
    # ---------------------------------------------------------
    # 1. Hospital Standardization (Sample Size Guardrail n >= 30)
    # ---------------------------------------------------------
    top_hospitals = set(df["hospital"].value_counts()[lambda x: x >= 30].index.tolist())
    df["hospital_facility"] = df["hospital"].apply(
        lambda x: x if x in top_hospitals else "Other Facilities (n < 30)"
    )
    
    # ---------------------------------------------------------
    # 2. Dim_Date (Calendar Dimension: 2019-01-01 to 2024-12-31)
    # ---------------------------------------------------------
    min_date = pd.to_datetime("2019-01-01")
    max_date = pd.to_datetime("2024-12-31")
    dates = pd.date_range(min_date, max_date, freq="D")
    
    dim_date = pd.DataFrame({
        "date_key": dates.strftime("%Y%m%d").astype(int),
        "date": dates.strftime("%Y-%m-%d"),
        "year": dates.year,
        "quarter": "Q" + dates.quarter.astype(str),
        "month_num": dates.month,
        "month_name": dates.strftime("%B"),
        "year_month": dates.strftime("%Y-%m"),
        "day_of_month": dates.day,
        "day_of_week": dates.strftime("%A"),
        "day_of_week_num": dates.dayofweek + 1,
        "is_weekend": dates.dayofweek.isin([5, 6]).astype(int)
    })
    dim_date_path = os.path.join(output_dir, "Dim_Date.csv")
    dim_date.to_csv(dim_date_path, index=False)
    print(f"Saved Dim_Date: {len(dim_date):,} rows -> {dim_date_path}")
    
    # ---------------------------------------------------------
    # 3. Dim_Condition (Medical Condition & Specialty Proxy)
    # ---------------------------------------------------------
    specialty_lookup = {
        "Asthma": "Pulmonology",
        "Cancer": "Oncology",
        "Diabetes": "Endocrinology",
        "Hypertension": "Cardiology",
        "Arthritis": "Rheumatology",
        "Obesity": "Bariatrics & Metabolism"
    }
    
    unique_conditions = sorted(df["medical_condition"].unique().tolist())
    dim_condition = pd.DataFrame({
        "medical_condition": unique_conditions,
        "clinical_specialty_proxy": [specialty_lookup.get(c, "General Medicine") for c in unique_conditions],
        "chronic_disease_flag": 1,
        "assumption_note": "Specialty inferred from primary diagnosis per field availability matrix"
    })
    dim_condition_path = os.path.join(output_dir, "Dim_Condition.csv")
    dim_condition.to_csv(dim_condition_path, index=False)
    print(f"Saved Dim_Condition: {len(dim_condition):,} rows -> {dim_condition_path}")

    # ---------------------------------------------------------
    # 4. Dim_Patient (De-identified Patient Dimension)
    # ---------------------------------------------------------
    patient_group = df.sort_values("admission_date").groupby("patient_key")
    dim_patient = patient_group.agg(
        age_at_first_stay=("age", "first"),
        age_group=("age_group", "first"),
        gender=("gender", "first"),
        blood_type=("blood_type", "first"),
        total_lifetime_admissions=("admission_id", "count"),
        first_admission_date=("admission_date", "first"),
        last_discharge_date=("discharge_date", "last")
    ).reset_index()
    
    dim_patient_path = os.path.join(output_dir, "Dim_Patient.csv")
    dim_patient.to_csv(dim_patient_path, index=False)
    print(f"Saved Dim_Patient: {len(dim_patient):,} unique patients -> {dim_patient_path}")

    # ---------------------------------------------------------
    # 5. Dim_Doctor (Pseudonymous Physician Dimension)
    # ---------------------------------------------------------
    doctor_group = df.groupby("doctor_id")
    dim_doctor = doctor_group.agg(
        total_cases=("admission_id", "count"),
        unique_patients_served=("patient_key", "nunique"),
        avg_los_days=("los_days", "mean")
    ).reset_index()
    dim_doctor["doctor_label"] = "Physician " + dim_doctor["doctor_id"]
    
    dim_doctor_path = os.path.join(output_dir, "Dim_Doctor.csv")
    dim_doctor.to_csv(dim_doctor_path, index=False)
    print(f"Saved Dim_Doctor: {len(dim_doctor):,} pseudonymous physicians -> {dim_doctor_path}")

    # ---------------------------------------------------------
    # 6. Dim_Hospital (Hospital Facility Dimension)
    # ---------------------------------------------------------
    hospital_group = df.groupby("hospital_facility")
    dim_hospital = hospital_group.agg(
        total_admissions=("admission_id", "count"),
        unique_patients_treated=("patient_key", "nunique"),
        total_billed_amount=("billing_amount", "sum"),
        avg_los_days=("los_days", "mean")
    ).reset_index()
    dim_hospital.rename(columns={"hospital_facility": "hospital"}, inplace=True)
    dim_hospital["qualification_tier"] = np.where(
        dim_hospital["hospital"] == "Other Facilities (n < 30)", 
        "Aggregated Other (n < 30)", 
        "Qualified Facility (n >= 30)"
    )
    dim_hospital_path = os.path.join(output_dir, "Dim_Hospital.csv")
    dim_hospital.to_csv(dim_hospital_path, index=False)
    print(f"Saved Dim_Hospital: {len(dim_hospital):,} facility tiers -> {dim_hospital_path}")

    # ---------------------------------------------------------
    # 7. Fact_Admissions (Core Inpatient Admissions Fact Table)
    # ---------------------------------------------------------
    fact_admissions = pd.DataFrame()
    fact_admissions["admission_id"] = df["admission_id"]
    fact_admissions["patient_key"] = df["patient_key"]
    fact_admissions["doctor_id"] = df["doctor_id"]
    fact_admissions["hospital"] = df["hospital_facility"]
    fact_admissions["medical_condition"] = df["medical_condition"]
    
    # Date foreign keys (YYYYMMDD integer)
    adm_dt = pd.to_datetime(df["admission_date"])
    dis_dt = pd.to_datetime(df["discharge_date"])
    fact_admissions["admission_date_key"] = adm_dt.dt.strftime("%Y%m%d").astype(int)
    fact_admissions["discharge_date_key"] = dis_dt.dt.strftime("%Y%m%d").astype(int)
    fact_admissions["admission_date"] = df["admission_date"]
    fact_admissions["discharge_date"] = df["discharge_date"]
    
    # Degenerate dimensions
    fact_admissions["admission_type"] = df["admission_type"]
    fact_admissions["insurance_provider"] = df["insurance_provider"]
    fact_admissions["room_number"] = df["room_number"]
    fact_admissions["medication"] = df["medication"]
    fact_admissions["test_results"] = df["test_results"]
    
    # Quantitative Measures & Flags
    fact_admissions["los_days"] = df["los_days"]
    fact_admissions["billing_amount"] = df["billing_amount"]
    fact_admissions["cost_per_day"] = df["cost_per_day"]
    fact_admissions["high_cost_flag"] = df["high_cost_flag"]
    fact_admissions["long_stay_flag"] = df["long_stay_flag"]
    fact_admissions["readmission_eligible"] = df["readmission_eligible"]
    fact_admissions["readmitted_30d"] = df["readmitted_30d"]
    fact_admissions["days_to_next_admission"] = df["days_to_next_admission"]
    
    fact_admissions_path = os.path.join(output_dir, "Fact_Admissions.csv")
    fact_admissions.to_csv(fact_admissions_path, index=False)
    print(f"Saved Fact_Admissions: {len(fact_admissions):,} rows -> {fact_admissions_path}")
    print("\n[SUCCESS] Power BI Star Schema tables successfully exported with sample size guardrails!")

if __name__ == "__main__":
    export_powerbi_star_schema()
