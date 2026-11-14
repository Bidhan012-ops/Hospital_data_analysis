# Executive Summary of Key Exploratory Findings

This document summarizes the core empirical findings derived from the exploratory data analysis of **54,966 clean inpatient admissions** (`data/processed/hospital_clean.csv`). Every finding is cross-referenced with its supporting figure artifact and verified by executable notebook cells.

---

### Finding 1: Symmetrical Demographic Age Distribution Across Adult Lifespan
* **Observed Metrics**: Patient ages range from 13 to 89 years with a mean of 51.54 years, a median of 52.0 years, and an interquartile range (IQR) of 33.0 years (skewness = -0.0057).
* **Clinical Context**: Inpatient distribution is remarkably uniform across adult cohorts; patients aged 65+ account for the largest single age bracket (30.8% of admissions, n = 16,923), followed by 50-64 (22.4%).
* **Supporting Visualization**: [`outputs/figures/eda_01_age_distribution.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_01_age_distribution.png) and [`outputs/figures/eda_02_age_group_counts.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_02_age_group_counts.png).

---

### Finding 2: Parity Across Patient Sex and ABO/Rh Phenotypes
* **Observed Metrics**: Gender split is virtually identical at 50.02% Male (n = 27,496) versus 49.98% Female (n = 27,470). Blood types are equally distributed across all 8 ABO/Rh categories (~12.5% each; range: 6,804 to 6,903 admissions).
* **Operational Implication**: Facility capacity planning does not need sex-specialized ward allocation adjustments for general medical admissions.
* **Supporting Visualization**: [`outputs/figures/eda_03_gender_split.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_03_gender_split.png) and [`outputs/figures/eda_04_blood_type_distribution.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_04_blood_type_distribution.png).

---

### Finding 3: Equiproportional Chronic Disease Inflow
* **Observed Metrics**: Inpatient volume is evenly balanced across the 6 tracked medical conditions: Arthritis (16.8%, n = 9,218), Diabetes (16.8%, n = 9,216), Hypertension (16.7%, n = 9,151), Obesity (16.6%, n = 9,146), Cancer (16.6%, n = 9,140), and Asthma (16.5%, n = 9,095).
* **Operational Implication**: Demonstrates a balanced chronic disease caseload without overwhelming diagnostic concentration in any single clinical service line.
* **Supporting Visualization**: [`outputs/figures/eda_06_medical_conditions.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_06_medical_conditions.png).

---

### Finding 4: Extreme Provider and Physician Fragmentation
* **Observed Metrics**: Admissions are distributed across 39,876 distinct hospital facility names and 40,341 distinct physician IDs. The highest-volume facility ('LLC Smith') treated only 44 patients (0.08% of total volume), while the highest-volume physician ('DR-27857') managed 27 admissions (0.05%).
* **Methodological Decision**: Physician-level and facility-level performance comparisons must enforce the $n \ge 30$ threshold. Only 12 hospitals reach $n \ge 30$, and zero physicians achieve $n \ge 30$, mandating aggregate rather than individual physician rate reporting.
* **Supporting Visualization**: [`outputs/figures/eda_07_top_hospitals.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_07_top_hospitals.png) and [`outputs/figures/eda_08_top_doctors.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_08_top_doctors.png).

---

### Finding 5: Uniform Payer Mix and Pharmaceutical Utilization
* **Observed Metrics**: Admissions are split evenly across 5 health insurance providers: Cigna (20.3%), Medicare (20.1%), UnitedHealthcare (20.0%), Blue Cross (19.9%), and Aetna (19.7%). Similarly, prescribed medications each account for approximately 20.0% of cases.
* **Financial Impact**: Payer risk is evenly diversified between commercial payers (~60%) and government Medicare coverage (~20%).
* **Supporting Visualization**: [`outputs/figures/eda_09_insurance_providers.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_09_insurance_providers.png) and [`outputs/figures/eda_10_medications.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_10_medications.png).

---

### Finding 6: Intake Acuity Distribution and Pediatric Emergency Skew
* **Observed Metrics**: In the general cohort, admission acuity is balanced between Elective (33.6%), Urgent (33.5%), and Emergency (32.9%). However, within pediatric admissions (age 0-17, n = 58), Emergency intake surges to 41.38% compared to 32.92% among adults.
* **Operational Implication**: Pediatric inpatient admissions predominantly enter through emergent channels rather than scheduled elective procedures.
* **Supporting Visualization**: [`outputs/figures/eda_12_admission_types_share.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_12_admission_types_share.png) and [`outputs/figures/eda_14_admission_type_by_age_group_heatmap.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_14_admission_type_by_age_group_heatmap.png).

---

### Finding 7: Stable Longitudinal Admission Inflow & Boundary Month Censoring
* **Observed Metrics**: Across the 59 fully observed calendar months (2019-06 through 2024-04), monthly admission volume is highly consistent, averaging 916.6 admissions per month (std = 32.5; range: 849 to 985). 
* **Methodological Flag**: May 2019 (677 admissions, starting May 8) and May 2024 (212 admissions, ending May 7) are verified as partial intake periods and flagged to prevent distorted monthly rate comparisons.
* **Supporting Visualization**: [`outputs/figures/eda_15_monthly_trends_rolling_avg.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_15_monthly_trends_rolling_avg.png) and [`outputs/figures/eda_16_yoy_comparison.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_16_yoy_comparison.png).

---

### Finding 8: Weekly Intake Equidistribution
* **Observed Metrics**: Day-of-week admissions show almost zero day-to-day variance, ranging from 7,781 on Mondays (14.16%) to 7,913 on Tuesdays (14.40%), with weekend admissions remaining robust (Saturday: 7,822; Sunday: 7,850).
* **Operational Takeaway**: Inpatient intake flows continuously throughout all 7 days without weekday surge clustering, reflecting synthetic intake modeling.
* **Supporting Visualization**: [`outputs/figures/eda_17_weekday_admissions.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_17_weekday_admissions.png).

---

### Finding 9: Overall Stay and Financial Baseline Metrics
* **Observed Metrics**: Overall ALOS is 15.50 days (median: 15.0 days, IQR: 15.0 days). Total gross billed charges exceed \$1.404 billion, with a mean cost per admission of \$25,544.31 (median: \$25,542.75) and an average cost per day of \$3,392.47.
* **Supporting Visualization**: [`outputs/figures/eda_01_age_distribution.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/eda_01_age_distribution.png) and [`outputs/tables/eda_summary_stats.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/eda_summary_stats.csv).

---

### Finding 10: Derived 30-Day Readmission Proxy Baseline
* **Observed Metrics**: Among the 53,566 admissions with complete 30-day post-discharge observation windows (`readmission_eligible = 1`), exactly 580 readmissions occurred within 30 days, establishing an overall baseline readmission rate of **1.08%**.
* **Supporting Reference**: Documented in canonical schema and verified in validation reporting.
