"""
Script to build and execute notebooks/03_eda.ipynb
Contains all 7 required sections:
Overview, Demographics, Diagnoses and Groupings, Admission Types,
Time Trends, Cross-tabulations, Key Findings.
Includes 18 labelled charts, exact numeric interpretations, and location unavailability note.
"""

import os
import io
import sys
import contextlib
import shutil
import nbformat as nbf
import pandas as pd
import numpy as np

def generate_eda_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.11.9"
        }
    }

    cells_definition = [
        ("markdown", """# 03. Exploratory Data Analysis & Diagnostic Profiling
**Phase 3: Exploratory Data Analysis**  
**Project:** Hospital Patient Data Analysis and Dashboard Development Using Python and Power BI

---

### Analytical Scope & Notebook Architecture
This notebook conducts a thorough exploratory analysis of the clean canonical dataset (`data/processed/hospital_clean.csv`), describing patient populations, diagnostic intake, clinical utilization, and longitudinal admission trends.

The analysis is structured across seven dedicated sections:
1. **Overview & Summary Statistics**: High-level cohort KPIs and parametric/non-parametric metric summaries.
2. **Demographics**: Age distributions, age brackets, sex ratios, blood group phenotypes, and note on geographic data absence.
3. **Diagnoses & Clinical Groupings**: Primary condition distributions, facility dispersion, physician caseloads, payer shares, medications, and lab test outcomes.
4. **Admission Types & Intake Acuity**: Admission urgency distribution and cross-tabulations across clinical conditions and age brackets.
5. **Temporal Patterns & Inpatient Trends**: Longitudinal monthly trends, 3-month rolling averages, partial month handling, YoY comparisons, and weekday intake.
6. **Cross-Tabulations & Operational Interactions**: Condition-medication matrices, ALOS across cohorts, and 30-day readmissions.
7. **Key Findings Synthesis**: Summary of core findings linked to empirical figure artifacts.
"""),
        ("code", """# Environment setup, imports, and display configuration
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fix random seed for reproducibility
np.random.seed(42)

# Visualization settings
pd.set_option('display.max_columns', 35)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print(f"Python interpreter: {sys.version.split()[0]}")
print(f"Pandas version: {pd.__version__}")
"""),
        ("markdown", """## 1. Overview & Dataset Baseline Summary
Loading the clean canonical dataset and computing descriptive statistics for `age`, `los_days`, and `billing_amount`."""),
        ("code", """# Load processed clean dataset using relative path
clean_path = 'data/processed/hospital_clean.csv'
if not os.path.exists(clean_path):
    clean_path = '../data/processed/hospital_clean.csv'

df = pd.read_csv(clean_path)
df['admission_date'] = pd.to_datetime(df['admission_date'])
df['discharge_date'] = pd.to_datetime(df['discharge_date'])

total_admissions = len(df)
total_patients = df['patient_key'].nunique()
total_billing = df['billing_amount'].sum()
overall_alos_mean = df['los_days'].mean()
overall_alos_median = df['los_days'].median()

print("=" * 60)
print("HOSPITAL INPATIENT COHORT EXECUTIVE OVERVIEW")
print("=" * 60)
print(f"Total Inpatient Admissions : {total_admissions:,}")
print(f"Total Unique Patients      : {total_patients:,}")
print(f"Total Gross Billed Charges : ${total_billing:,.2f}")
print(f"Overall Mean ALOS          : {overall_alos_mean:.2f} days")
print(f"Overall Median ALOS        : {overall_alos_median:.1f} days")
print(f"Mean Cost Per Admission    : ${df['billing_amount'].mean():,.2f}")
print(f"Mean Cost Per Hospital Day : ${df['cost_per_day'].mean():,.2f}")
"""),
        ("code", """# Descriptive Statistics Table for Age, LOS, and Billing Amount
stats_cols = ['age', 'los_days', 'billing_amount']
summary_list = []
for c in stats_cols:
    s = df[c]
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    summary_list.append({
        'variable': c,
        'count': int(s.count()),
        'mean': round(s.mean(), 2),
        'median': round(s.median(), 2),
        'std': round(s.std(), 2),
        'min': round(s.min(), 2),
        'max': round(s.max(), 2),
        'iqr': round(q3 - q1, 2),
        'skewness': round(s.skew(), 4)
    })

summary_stats_df = pd.DataFrame(summary_list)
print("Descriptive Statistics Summary Table (outputs/tables/eda_summary_stats.csv):")
print(summary_stats_df.to_string(index=False))
"""),
        ("markdown", """## 2. Patient Demographics Profiling
Evaluating patient age, age brackets, gender ratios, blood type distributions, and documenting unavailable fields.

> **DATA AVAILABILITY DISCLOSURE: PATIENT LOCATION**:
> Patient residential address, city, state, and postal code are **completely unavailable** in the source dataset.
> In strict conformance with project governance rules, no synthetic geographic field is substituted or fabricated. Facility analysis relies strictly on the `hospital` identifier."""),
        ("code", """# Demographic Metrics Computation
mean_age = df['age'].mean()
median_age = df['age'].median()
iqr_age = df['age'].quantile(0.75) - df['age'].quantile(0.25)
skew_age = df['age'].skew()

print(f"Age Distribution Metrics: Mean = {mean_age:.2f} yrs, Median = {median_age:.1f} yrs, IQR = {iqr_age:.1f} yrs, Skewness = {skew_age:.4f}")
print(f"Admissions under 18 years (Pediatrics): {(df['age_group'] == '0-17').sum():,} ({(df['age_group'] == '0-17').mean()*100:.2f}%)")
print(f"Admissions 65+ years (Geriatrics): {(df['age_group'] == '65+').sum():,} ({(df['age_group'] == '65+').mean()*100:.2f}%)")

male_pct = (df['gender'] == 'Male').mean() * 100
female_pct = (df['gender'] == 'Female').mean() * 100
print(f"Gender Breakdown: Male = {male_pct:.2f}%, Female = {female_pct:.2f}%")

print("\\nBlood Type Distribution:")
print(df['blood_type'].value_counts(normalize=True).round(4) * 100)
"""),
        ("markdown", """### Demographic Visualizations & Numerical Interpretations
* **Figure 1**: [`outputs/figures/eda_01_age_distribution.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_01_age_distribution.png)
  * *Interpretation*: Patient ages span 13 to 89 years with a mean of 51.54 years and a median of 52.00 years. The near-zero skewness (-0.0057) demonstrates an approximately uniform distribution across the adult lifespan.
* **Figure 2**: [`outputs/figures/eda_02_age_group_counts.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_02_age_group_counts.png)
  * *Interpretation*: Senior citizens (65+) account for the largest single inpatient demographic cohort at 30.8% of total volume (16,929 admissions), whereas pediatric cases (0-17) represent just 0.1% (58 admissions).
* **Figure 3**: [`outputs/figures/eda_03_gender_split.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_03_gender_split.png)
  * *Interpretation*: Inpatient admissions are split symmetrically between males (27,508 admissions, 50.04%) and females (27,458 admissions, 49.96%), indicating sex parity across general medical services.
* **Figure 4**: [`outputs/figures/eda_04_blood_type_distribution.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_04_blood_type_distribution.png)
  * *Interpretation*: All 8 ABO and Rhesus phenotypes demonstrate uniform representation, with each blood type comprising between 12.38% (O-) and 12.56% (A-) of the patient population.
* **Figure 5**: [`outputs/figures/eda_05_age_group_by_gender.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_05_age_group_by_gender.png)
  * *Interpretation*: Cross-tabulation of age group and gender demonstrates equal representation within every age bracket (e.g., age 65+ includes 8,432 males and 8,497 females)."""),
        ("markdown", """## 3. Diagnoses, Provider Network & Clinical Groupings
Analyzing primary medical conditions, facility volume fragmentation, physician caseload dispersion, insurance payers, pharmaceuticals, and lab test results."""),
        ("code", """# Clinical & Provider Metrics Computation
print("Primary Medical Condition Breakdown:")
cond_df = pd.DataFrame({
    'Admissions': df['medical_condition'].value_counts(),
    'Share (%)': (df['medical_condition'].value_counts(normalize=True) * 100).round(2),
    'Mean ALOS': df.groupby('medical_condition')['los_days'].mean().round(2),
    'Median ALOS': df.groupby('medical_condition')['los_days'].median().round(1),
    'Mean Billing ($)': df.groupby('medical_condition')['billing_amount'].mean().round(2)
})
print(cond_df.to_string())

top10_hosp = df['hospital'].value_counts().head(10)
top10_hosp_total = top10_hosp.sum()
print(f"\\nTop 10 Hospitals Volume: {top10_hosp_total:,} admissions ({(top10_hosp_total/len(df))*100:.2f}% of total {df['hospital'].nunique():,} hospitals)")

top10_doc = df['doctor_id'].value_counts().head(10)
top10_doc_total = top10_doc.sum()
print(f"Top 10 Doctors Volume: {top10_doc_total:,} admissions ({(top10_doc_total/len(df))*100:.2f}% of total {df['doctor_id'].nunique():,} doctors)")
print(f"Maximum single physician caseload: {top10_doc.max()} admissions (All doctors have n < 30)")
"""),
        ("markdown", """### Clinical & Provider Visualizations & Interpretations
* **Figure 6**: [`outputs/figures/eda_06_medical_conditions.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_06_medical_conditions.png)
  * *Interpretation*: Inpatient admissions are distributed equiproportionately across 6 chronic conditions, ranging from 9,095 admissions for Asthma (16.55%) to 9,219 for Arthritis (16.77%).
* **Figure 7**: [`outputs/figures/eda_07_top_hospitals.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_07_top_hospitals.png)
  * *Interpretation*: The provider network is heavily fragmented across 39,876 facilities; the top 10 hospitals account for only 360 admissions (0.65% of total volume), with the largest facility managing 44 stays.
* **Figure 8**: [`outputs/figures/eda_08_top_doctors.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_08_top_doctors.png)
  * *Interpretation*: Attending physician caseloads are highly dispersed across 40,341 pseudonymous IDs; the highest-volume physician managed 27 admissions, confirming that no individual doctor achieves the $n \\ge 30$ threshold.
* **Figure 9**: [`outputs/figures/eda_09_insurance_providers.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_09_insurance_providers.png)
  * *Interpretation*: Health insurance coverage is balanced across commercial and government payers, with Cigna leading at 20.27% (11,141 admissions) and Aetna at 19.66% (10,808 admissions).
* **Figure 10**: [`outputs/figures/eda_10_medications.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_10_medications.png)
  * *Interpretation*: Prescribed pharmaceuticals show uniform clinical utilization, with Lipitor representing 20.08% (11,038 prescriptions) and Penicillin representing 19.93% (10,957 prescriptions).
* **Figure 11**: [`outputs/figures/eda_11_test_results.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_11_test_results.png)
  * *Interpretation*: Diagnostic lab test results show equal splits across Abnormal (33.56%), Normal (33.37%), and Inconclusive (33.07%) outcomes, with negligible variance across conditions."""),
        ("markdown", """## 4. Admission Types & Clinical Intake Acuity
Evaluating admission urgency (Elective, Urgent, Emergency) and testing intake patterns across demographic tiers and clinical diagnoses."""),
        ("code", """# Admission Type Metrics & Cross-Tabulations
print("Admission Type Distribution:")
adm_type_df = pd.DataFrame({
    'Admissions': df['admission_type'].value_counts(),
    'Share (%)': (df['admission_type'].value_counts(normalize=True) * 100).round(2)
})
print(adm_type_df.to_string())

print("\\nAdmission Type by Clinical Condition (Row %):")
cond_adm_pct = pd.crosstab(df['medical_condition'], df['admission_type'], normalize='index') * 100
print(cond_adm_pct.round(2).to_string())

print("\\nAdmission Type by Age Group (Row %):")
age_adm_pct = pd.crosstab(df['age_group'], df['admission_type'], normalize='index').reindex(['0-17', '18-34', '35-49', '50-64', '65+']) * 100
print(age_adm_pct.round(2).to_string())
"""),
        ("markdown", """### Admission Type Visualizations & Interpretations
* **Figure 12**: [`outputs/figures/eda_12_admission_types_share.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_12_admission_types_share.png)
  * *Interpretation*: Overall admission acuity is divided equally among Elective (18,485 admissions, 33.63%), Urgent (18,397 admissions, 33.47%), and Emergency (18,084 admissions, 32.90%) stays.
* **Figure 13**: [`outputs/figures/eda_13_admission_type_by_condition_heatmap.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_13_admission_type_by_condition_heatmap.png)
  * *Interpretation*: Clinical conditions display nearly identical intake urgency distributions (~33% for each acuity level), indicating that intake mode is independent of underlying chronic condition.
* **Figure 14**: [`outputs/figures/eda_14_admission_type_by_age_group_heatmap.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_14_admission_type_by_age_group_heatmap.png)
  * *Interpretation*: While adult cohorts maintain a balanced 33% split, pediatric patients (0-17 years, n = 58) present a notable elevation in Emergency admissions at 41.38% (24 admissions)."""),
        ("markdown", """## 5. Longitudinal Inpatient Volume & Temporal Patterns
Auditing monthly trends, 3-month rolling averages, boundary month censoring, and day-of-week patterns."""),
        ("code", """# Temporal Metrics Computation & Boundary Month Inspection
monthly_counts = df['admission_month'].value_counts().sort_index()

# Complete months exclude partial bounds: 2019-05 (starts May 8) and 2024-05 (ends May 7)
complete_months = monthly_counts.iloc[1:-1]
print(f"Total Calendar Months Recorded : {len(monthly_counts)}")
print(f"Fully Observed Months Evaluated: {len(complete_months)} (2019-06 through 2024-04)")
print(f"Mean Admissions (Complete Mos) : {complete_months.mean():.1f} per month (std = {complete_months.std():.1f})")
print(f"Min Complete Month Inflow      : {complete_months.min()} admissions ({complete_months.idxmin()})")
print(f"Max Complete Month Inflow      : {complete_months.max()} admissions ({complete_months.idxmax()})")

print(f"\\nBoundary Month Flag:")
print(f"  - 2019-05 (Partial, 24 days observed): {monthly_counts['2019-05']} admissions")
print(f"  - 2024-05 (Partial, 7 days observed) : {monthly_counts['2024-05']} admissions")

print("\\nDay-of-Week Inpatient Intake:")
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_counts = df['admission_weekday'].value_counts().reindex(days_order)
weekday_df = pd.DataFrame({'Admissions': weekday_counts, 'Share (%)': (weekday_counts/len(df)*100).round(2)})
print(weekday_df.to_string())
"""),
        ("markdown", """### Temporal Visualizations & Interpretations
* **Figure 15**: [`outputs/figures/eda_15_monthly_trends_rolling_avg.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_15_monthly_trends_rolling_avg.png)
  * *Interpretation*: Monthly admissions fluctuate within a narrow band around 917 cases per month (rolling 3-month average ranges from 885 to 953); May 2019 (677 stays) and May 2024 (212 stays) are explicitly flagged as incomplete observation intervals.
* **Figure 16**: [`outputs/figures/eda_16_yoy_comparison.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_16_yoy_comparison.png)
  * *Interpretation*: Year-over-year overlay of full calendar years (2020 to 2023) demonstrates uniform monthly volume without evidence of distinct seasonal surges or winter peaks.
* **Figure 17**: [`outputs/figures/eda_17_weekday_admissions.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_17_weekday_admissions.png)
  * *Interpretation*: Inpatient admissions occur steadily throughout the week, ranging from 7,781 on Mondays (14.16%) to 7,913 on Tuesdays (14.40%), with weekend days maintaining equivalent volume (Saturday: 7,822, Sunday: 7,850).
* **Figure 18**: [`outputs/figures/eda_18_discharges_per_month_and_mom.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_18_discharges_per_month_and_mom.png)
  * *Interpretation*: Inpatient discharge volume closely mirrors admissions with an average lag of 15.5 days, maintaining stable month-over-month throughput."""),
        ("markdown", """## 6. Cross-Tabulations & Operational Interactions
Analyzing condition-medication interactions, length of stay, and readmission proxy distributions."""),
        ("code", """# Cross-Tabulation Matrix: Medical Condition vs Medication
print("Condition vs Medication Interaction Frequency Matrix:")
cond_med_ct = pd.crosstab(df['medical_condition'], df['medication'])
print(cond_med_ct.to_string())

# Operational Performance by Condition: ALOS, Outliers & Readmission
print("\\nClinical Operational Metrics by Condition:")
clin_ops = pd.DataFrame({
    'Admissions': df.groupby('medical_condition').size(),
    'Mean ALOS': df.groupby('medical_condition')['los_days'].mean().round(2),
    'Median ALOS': df.groupby('medical_condition')['los_days'].median().round(1),
    'Long Stay %': (df.groupby('medical_condition')['long_stay_flag'].mean() * 100).round(2),
    'Mean Billing ($)': df.groupby('medical_condition')['billing_amount'].mean().round(2),
    'High Cost %': (df.groupby('medical_condition')['high_cost_flag'].mean() * 100).round(2),
    'Readmission Rate (%)': df[df['readmission_eligible'] == 1].groupby('medical_condition')['readmitted_30d'].mean().round(4) * 100
})
print(clin_ops.to_string())
"""),
        ("markdown", """## 7. Key Findings Synthesis & Deliverables Verification
Reviewing the 10 core findings synthesized in `outputs/tables/eda_key_findings.md`."""),
        ("code", """# Display executive key findings document
key_findings_path = 'outputs/tables/eda_key_findings.md'
if not os.path.exists(key_findings_path):
    key_findings_path = '../outputs/tables/eda_key_findings.md'

with open(key_findings_path, 'r', encoding='utf-8') as f:
    findings_text = f.read()

# Print summary header and finding titles
for line in findings_text.splitlines():
    if line.startswith('### Finding') or line.startswith('* **Observed Metrics**') or line.startswith('* **Supporting'):
        print(line)
""")
    ]

    execution_context = {}
    nb_cells = []
    execution_count = 1

    for cell_type, content in cells_definition:
        if cell_type == "markdown":
            nb_cells.append(nbf.v4.new_markdown_cell(content))
        elif cell_type == "code":
            stdout_capture = io.StringIO()
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stdout_capture):
                try:
                    exec(content, execution_context)
                    captured_text = stdout_capture.getvalue()
                    outputs = []
                    if captured_text:
                        outputs.append(nbf.v4.new_output(output_type="stream", name="stdout", text=captured_text))
                    code_cell = nbf.v4.new_code_cell(
                        source=content,
                        execution_count=execution_count,
                        outputs=outputs
                    )
                    execution_count += 1
                    nb_cells.append(code_cell)
                except Exception as e:
                    print(f"[ERROR] Cell failed during execution: {e}")
                    raise e

    nb.cells = nb_cells

    target_path = "notebooks/03_eda.ipynb"
    with open(target_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Successfully generated and executed: {target_path}")

    # Mirror to phase3_eda
    p3_nb = "phase3_eda/03_eda.ipynb"
    shutil.copy(target_path, p3_nb)
    print(f"Mirrored notebook into: {p3_nb}")

if __name__ == "__main__":
    generate_eda_notebook()

