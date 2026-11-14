# Executive Key Findings: Cost and Billing Analysis

This document synthesizes the diagnostic findings from **Phase 5: Cost and Billing Analysis** conducted on **54,966 inpatient admissions** (`data/processed/hospital_clean.csv`). Every metric is cross-referenced with empirical tables and figures.

---

### Finding 1: Billing Baseline & Per-Admission vs. Per-Patient Dual Metric Accounting
* **Observed Metrics**: Total gross billed charges across the network equal **1,404,068,339.23 currency units (CU)**.
  * **Cost per Admission (Mean)**: **25,544.31 CU** (Median: 25,542.75 CU, Std: 14,208.41 CU). Used for episode-of-care cost tracking.
  * **Cost per Patient (Mean)**: **34,896.69 CU** across 40,235 unique patient keys. Used for longitudinal patient population financial liability. The per-patient average is 9,352.38 CU higher due to multi-stay utilization.
  * **Cost per Day (`cost_per_day`)**: Mean is **3,392.47 CU/day**; Median is **1,649.59 CU/day**.
* **Currency Labeling**: Currency is unspecified in the source Kaggle data; all figures are uniformly denoted as **Currency Units (CU)**.
* **Negative & Zero Billing Handling**: Exactly 106 records contain negative billing amounts (range: -2,008.49 to -0.01 CU). Zero records have zero billing. In strict compliance with the project's non-deletion policy, these 106 records were retained and flagged (`billing_outlier_flag = 1`) to preserve audit trail integrity while enabling filtered sensitivity analyses.
* **Supporting Artifacts**: [`outputs/tables/cost_by_insurance_provider.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/cost_by_insurance_provider.csv) and [`outputs/figures/cost_01_distribution_linear_log.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/cost_01_distribution_linear_log.png).

---

### Finding 2: Payer Financial Parity & Lack of Claims Settlement Data
* **Observed Metrics**: Gross billed charges are distributed with near-perfect equivalence across the 5 insurance payers (~20% billing share each):
  * Medicare: 282.91M CU (20.15%, Mean: 25,628.32 CU, Median: 25,629.33 CU)
  * Blue Cross: 280.41M CU (19.97%, Mean: 25,603.46 CU, Median: 25,580.54 CU)
  * Aetna: 276.50M CU (19.69%, Mean: 25,549.69 CU, Median: 25,765.38 CU)
  * Cigna: 284.33M CU (20.25%, Mean: 25,526.00 CU, Median: 25,537.18 CU)
  * UnitedHealthcare: 279.92M CU (19.94%, Mean: 25,414.51 CU, Median: 25,222.11 CU)
* **Statistical Verification**: Kruskal-Wallis test ($H = 1.5028, df = 4, p = 0.8261, \eta^2 = -0.000045$) confirms no significant difference in billed charges between public and commercial payers. Bootstrap 95% CIs for all 5 providers overlap tightly in the [25,250 to 25,890] range.
* **Data Availability Disclosure: Payment Status**: Payment status (paid, pending, denied, copay) is **completely unavailable** in the raw dataset. All financial metrics reflect gross billed charges, not contractual net realization.
* **Supporting Artifacts**: [`outputs/tables/cost_by_insurance_provider.csv`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/tables/cost_by_insurance_provider.csv) and [`outputs/figures/cost_02_billing_by_payer.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/cost_02_billing_by_payer.png).

---

### Finding 3: High-Cost Case Profile & Threshold Specification
* **Observed Metrics**: Per project definitions, `high_cost_flag` identifies admissions at or above the 95th percentile threshold: **47,638.27 CU**.
* **Volume**: Exactly **2,749 admissions** (5.00%) are designated high-cost cases.
* **Profile Across Tiers**: High-cost stays occur uniformly across admission urgency (Emergency: 5.06%, Elective: 4.97%, Urgent: 4.96%; $\chi^2 = 0.5673, p = 0.7530, V = 0.0032$) and across medical conditions (ranging from 4.77% in Hypertension to 5.25% in Diabetes; $\chi^2 = 4.1173, p = 0.5327, V = 0.0087$).
* **Supporting Artifacts**: [`outputs/figures/cost_03_high_cost_profile.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/cost_03_high_cost_profile.png).

---

### Finding 4: Inpatient Pareto Curve Decoupling (Linear vs. 80/20 Rule)
* **Observed Metrics**: In contrast to standard healthcare expenditure curves where 20% of patients drive 80% of costs, this cohort displays a much flatter concentration:
  * The top 10% of admissions (5,496 stays) generate **18.68%** of total billing.
  * The top 20% of admissions (10,993 stays) generate **35.42%** of total billing.
* **Analytical Diagnosis**: Billed charges follow an artificially uniform distribution bounded between $0 and $52,764 CU. Extreme catastrophic outlier cases do not exist.
* **Supporting Artifacts**: [`outputs/figures/cost_04_pareto_curve.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/cost_04_pareto_curve.png).

---

### Finding 5: Complete Decoupling Between Stay Duration and Billed Charges
* **Observed Metrics**: Spearman rank correlation between inpatient length of stay (`los_days`) and billed charges (`billing_amount`) is **$\rho = -0.0048$** (95% CI: [-0.0132, 0.0035], $p = 0.2559$).
* **Operational Implication**: Stay duration does not predict or scale billed amounts. A 1-day stay and a 30-day stay have identical expected gross charges (~25,500 CU), causing median daily cost (`cost_per_day`) to decline precipitously from 25,500 CU/day for 1-day stays down to 850 CU/day for 30-day stays.
* **Supporting Artifacts**: [`outputs/figures/cost_05_los_vs_billing_hexbin.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/cost_05_los_vs_billing_hexbin.png) and [`outputs/figures/cost_06_cost_per_day_by_condition.png`](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/outputs/figures/cost_06_cost_per_day_by_condition.png).

---

### Strategic Cost-Control Questions for Hospital Management
Rather than drawing premature causal conclusions, the following operational questions are framed for executive consideration:

1. **Charge-Capture Decoupling**: *Given that stay duration (`los_days`) has zero correlation with billed charges ($\rho = -0.0048$), what charge-master and itemized billing audits should administration institute to align pricing with clinical intensity, nursing hours, and bed utilization?*
2. **Payer Contracting & Denial Tracking**: *Because all 5 insurance payers generate identical gross billing averages (~25,500 CU), what systems must be deployed to capture actual contractual adjustments, denial rates, and net cash collections per payer?*
3. **High-Cost Outlier Management**: *With high-cost admissions strictly bounded above 47,638.27 CU (2,749 cases), should clinical case-management review be targeted specifically at admissions exceeding 47,600 CU to review pharmaceutical and laboratory utilization?*
4. **Daily Cost Efficiency**: *How should hospital finance account for same-day and short-stay admissions where fixed intake charges cause `cost_per_day` to surge above 15,000 CU/day compared to extended stays?*
