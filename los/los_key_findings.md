# Executive Key Findings: Length of Stay (ALOS) Analysis

This document synthesizes the diagnostic findings from **Phase 4: Length of Stay Analysis** conducted on **54,966 inpatient admissions** (`data/processed/hospital_clean.csv`). Every metric is cross-referenced with empirical tables and figures.

---

### Finding 1: Overall Stay Baseline & Skewness Discussion
* **Observed Metrics**: Overall Average Length of Stay (ALOS) is **15.50 days** with a standard deviation of 8.66 days. The median LOS is **15.0 days** with an IQR of 15.0 days (range: 1 to 30 days).
* **Skewness & Median Reporting**: The sample skewness is **0.0028** (near zero), differing markedly from real-world hospital length of stay which is notoriously right-skewed with long tails. Because hospital stays are naturally bounded between 1 and 30 days in this dataset, mean and median align perfectly at ~15.0-15.5 days. Both are reported throughout to comply with healthcare reporting governance.
* **Supporting Artifacts**: [`outputs/tables/los_by_admission_type.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_by_admission_type.csv) and [`outputs/figures/los_01_distribution_histogram.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/los_01_distribution_histogram.png).

---

### Finding 2: Statistical Invariance Across Admission Acuity
* **Observed Metrics**: ALOS across admission types displays virtually identical durations: Elective = 15.56 days (95% CI: [15.44, 15.68]), Urgent = 15.51 days (95% CI: [15.38, 15.63]), and Emergency = 15.42 days (95% CI: [15.29, 15.54]).
* **Hypothesis Testing**: Kruskal-Wallis test ($H = 4.0310, df = 2, p = 0.1333, \eta^2 = 0.000037$) fails to reject $H_0$.
* **Practical Significance**: The maximum difference across urgency tiers is **0.14 days** (~3.4 hours), which is clinically and administratively meaningless. Hospital intake acuity does not dictate inpatient bed occupancy duration in this dataset.
* **Supporting Artifacts**: [`outputs/figures/los_02_by_admission_type.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/los_02_by_admission_type.png) and [`outputs/tables/los_stat_tests.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_stat_tests.csv).

---

### Finding 3: Clinical Diagnostic Invariance
* **Observed Metrics**: Length of stay across the 6 primary clinical conditions demonstrates uniformity: Asthma ALOS = 15.58 d (median: 15.0), Arthritis = 15.54 d, Cancer = 15.53 d, Diabetes = 15.48 d, Hypertension = 15.48 d, and Obesity = 15.44 d.
* **Hypothesis Testing & Pairwise Holm Adjustment**: Kruskal-Wallis test ($H = 5.2159, df = 5, p = 0.3901, \eta^2 = 0.000004$) indicates no significant difference. Pairwise Mann-Whitney tests across all 15 clinical pairs yield Holm-adjusted p-values of **1.0000**.
* **Practical Significance**: Maximum delta is **0.14 days** between Asthma and Obesity. Chronic condition category does not influence stay duration.
* **Supporting Artifacts**: [`outputs/figures/los_03_by_medical_condition.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/los_03_by_medical_condition.png) and [`outputs/tables/los_by_medical_condition.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_by_medical_condition.csv).

---

### Finding 4: Sex Parity Across Stay Durations
* **Observed Metrics**: Male patients experienced an ALOS of 15.54 days (median: 15.0 d, 95% CI: [15.44, 15.64]) compared to 15.46 days for females (median: 15.0 d, 95% CI: [15.36, 15.56]).
* **Hypothesis Testing**: Mann-Whitney U test ($U = 379,504,456.5, p = 0.3205$) confirms no statistically significant difference ($r_{rb} = -0.0049$).
* **Practical Significance**: Difference in average stay between sexes is **0.08 days** (~1.9 hours), confirming biological sex is unrelated to hospital stay length.
* **Supporting Artifacts**: [`outputs/tables/los_by_gender.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_by_gender.csv) and [`outputs/tables/los_stat_tests.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_stat_tests.csv).

---

### Finding 5: Independence of Patient Age and Stay Duration
* **Observed Metrics**: Spearman rank correlation between patient age (13 to 89 years) and stay duration is $\rho = 0.0079$ (95% CI: [-0.0004, 0.0163], $p = 0.0635$).
* **Practical Significance**: Age explains less than 0.01% of stay duration variance. Pediatric and geriatric patients experience identical median stays of 15.0 days.
* **Supporting Artifacts**: [`outputs/tables/los_by_age_group.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_by_age_group.csv).

---

### Finding 6: Long-Stay Profile Characterization (90th Percentile)
* **Observed Metrics**: The 90th percentile threshold for extended stays is **28 days**. Exactly **5,531 admissions** (10.06%) are classified as long stays (`long_stay_flag = 1`).
* **Subgroup Distribution**:
  * Condition: Asthma has highest proportion (10.84%, n=986), Obesity lowest (9.74%, n=891).
  * Urgency: Emergency = 10.24% (n=1,853), Elective = 10.19% (n=1,883), Urgent = 9.76% (n=1,795).
  * Age Group: 35-49 = 10.18%, 65+ = 10.09%, 50-64 = 10.04%, 18-34 = 9.96%, 0-17 = 8.62%.
* **Supporting Artifacts**: [`outputs/tables/los_long_stay_profile.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_long_stay_profile.csv).

---

### Finding 7: Provider Facility Benchmarking Guardrail ($n \ge 30$)
* **Observed Metrics**: Applying the mandatory $n \ge 30$ threshold restricts hospital facility ALOS reporting to exactly **12 facilities** out of 39,876. 
* **Facility Range**: Among qualified facilities, ALOS ranges from 12.82 days (Johnson Inc, n=34) to 18.06 days (Smith Ltd, n=37). All 39,864 smaller facilities ($n < 30$) are excluded to prevent spurious small-sample ranking.
* **Supporting Artifacts**: [`outputs/tables/los_by_hospital.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/los_by_hospital.csv).

---

### Limitations & Methodological Constraints
1. **Synthetic Nature**: The dataset reflects an artificially generated discrete uniform distribution [1, 30] for stay duration. Real-world hospital LOS typically exhibits heavy right-skewness and strong clinical differentiation (e.g., ICU stays, acute myocardial infarction vs. outpatient-equivalent observation).
2. **Absence of Clinical Severity**: Crucial clinical determinants of stay duration (comorbidity index, vital signs, lab values, ICU days, surgical complications, and discharge destination) are absent.
3. **No Clinical Causality**: All findings denote observational associations and synthetic properties; they must never be interpreted as clinical guidelines or treatment effects.
