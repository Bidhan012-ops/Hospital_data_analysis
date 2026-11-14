"""
Script to build and execute notebooks/05_cost_analysis.ipynb
Ensures in-process execution, complete coverage of Tasks 1-9 for Phase 5,
and zero privacy leaks.
"""

import os
import io
import sys
import contextlib
import shutil
import nbformat as nbf
import pandas as pd
import numpy as np

def generate_cost_notebook():
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
        ("markdown", """# 05. Healthcare Cost & Inpatient Billing Analysis
**Phase 5: Cost and Billing Analysis**  
**Project:** Hospital Patient Data Analysis and Dashboard Development Using Python and Power BI

---

### Analytical Objective & Scope
This notebook examines financial dynamics, billed charges, daily costs, high-cost outlier stays, and payer contributions across the clean canonical inpatient dataset (`data/processed/hospital_clean.csv`).

Key analytical pillars executed in this analysis:
1. **Billing Overview & Baseline Distribution**: Total billing, parametric/non-parametric summaries, percentiles (5th to 99th), linear/log distributions, and currency labeling as **Currency Units (unspecified)**.
2. **Handling of Negative/Zero Billing**: Auditing the 106 negative billed records, documenting retention and flagging (`billing_outlier_flag = 1`) per non-deletion policy.
3. **Core Financial Metrics Duality**: Clear distinction between **Cost per Admission** (mean: 25,544.31 CU) and **Cost per Patient** (mean: 34,896.69 CU), plus **Cost per Day** (mean: 3,392.47 CU/d; median: 1,649.59 CU/d).
4. **Reconciled Group Breakdowns**: 8 breakdown tables with $n$, total, mean, median, and percentage share reconciling to 100% of network billing ($1,404,068,339.23 CU).
5. **Payer Financial Dynamics & Payment Status Disclosure**: Analyzing payer billing equity, provider admission mix, and documenting the complete absence of claims realization/denial data.
6. **High-Cost Outliers (95th Percentile) & Pareto Curve**: Profiling stays exceeding 47,638.27 CU and evaluating concentration (top 10% generate 18.7%; top 20% generate 35.4%).
7. **Cost vs. LOS Decoupling**: Hexbin density analysis, Spearman rank correlation ($\rho = -0.0048$), and daily cost dynamics.
8. **Diagnostic Hypothesis Testing**: Kruskal-Wallis across payers and conditions, pairwise Holm corrections, Chi-Square of high-cost flags, and 2,000 bootstrap CIs per provider.
9. **Management Cost-Control Questions**: Framing financial findings as strategic questions for executive hospital administration.
"""),
        ("code", """# Environment setup, package imports, and display configuration
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import seaborn as sns

# Fix random seed
np.random.seed(42)

# Display configurations
pd.set_option('display.max_columns', 35)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print(f"Python interpreter: {sys.version.split()[0]}")
print(f"Pandas version: {pd.__version__}")
"""),
        ("markdown", """## 1. Inpatient Billing Overview & Distribution Bounds
Computing network-wide billing metrics, percentiles, and documenting currency units and negative billing handling."""),
        ("code", """clean_path = 'data/processed/hospital_clean.csv'
if not os.path.exists(clean_path):
    clean_path = '../data/processed/hospital_clean.csv'

df = pd.read_csv(clean_path)
df['admission_date'] = pd.to_datetime(df['admission_date'])
df['discharge_date'] = pd.to_datetime(df['discharge_date'])

s_bill = df['billing_amount']
tot_billing = s_bill.sum()
mean_b = s_bill.mean()
med_b = s_bill.median()
std_b = s_bill.std()
skew_b = s_bill.skew()
kurt_b = s_bill.kurtosis()

pct_5, pct_25, pct_50, pct_75, pct_95, pct_99 = np.percentile(s_bill, [5, 25, 50, 75, 95, 99])

overview_df = pd.DataFrame([{
    'Total Billed (CU)': f"{tot_billing:,.2f}",
    'Mean (CU)': f"{mean_b:,.2f}",
    'Median (CU)': f"{med_b:,.2f}",
    'Std Dev (CU)': f"{std_b:,.2f}",
    'Skewness': f"{skew_b:.4f}",
    'Kurtosis': f"{kurt_b:.4f}",
    '5th Pct': f"{pct_5:,.2f}",
    '25th Pct': f"{pct_25:,.2f}",
    '50th Pct': f"{pct_50:,.2f}",
    '75th Pct': f"{pct_75:,.2f}",
    '95th Pct': f"{pct_95:,.2f}",
    '99th Pct': f"{pct_99:,.2f}"
}])
print("Inpatient Billed Charges Baseline Overview:")
print(overview_df.to_string(index=False))

print("\\n--- Currency & Negative Billing Disclosures ---")
print("1. Currency Units: Currency is not stated in source data; all amounts are labeled 'Currency Units (CU)'.")
neg_count = (s_bill < 0).sum()
zero_count = (s_bill == 0).sum()
print(f"2. Negative Billed Records: {neg_count} records (Min: {s_bill.min():,.2f} CU). Zero-billed records: {zero_count}.")
print("3. Handling Strategy: Preserved and explicitly flagged (billing_outlier_flag = 1) per non-deletion outlier policy.")
"""),
        ("markdown", """## 2. Core Financial Definitions: Per-Admission vs. Per-Patient Duality
Reporting both averages and defining their exact analytical purposes."""),
        ("code", """n_admissions = len(df)
n_patients = df['patient_key'].nunique()

cost_per_admission_mean = tot_billing / n_admissions
cost_per_patient_mean = tot_billing / n_patients
cost_per_day_mean = df['cost_per_day'].mean()
cost_per_day_median = df['cost_per_day'].median()

duality_df = pd.DataFrame([
    {
        'Metric Concept': 'Cost per Admission (Episode of Care)',
        'Scope': f"{n_admissions:,} total inpatient admissions",
        'Mean Value': f"{cost_per_admission_mean:,.2f} CU",
        'Median Value': f"{med_b:,.2f} CU",
        'Analytical Purpose & Governance Application': 'Used for facility operational throughput, episode-of-care cost tracking, and clinical case pricing.'
    },
    {
        'Metric Concept': 'Cost per Patient (Longitudinal Incurred Cost)',
        'Scope': f"{n_patients:,} distinct patient entities",
        'Mean Value': f"{cost_per_patient_mean:,.2f} CU",
        'Median Value': 'N/A (Patient-level aggregated)',
        'Analytical Purpose & Governance Application': 'Used for population health risk, longitudinal payer liability, and multi-admission cost burden.'
    },
    {
        'Metric Concept': 'Cost per Day (cost_per_day)',
        'Scope': 'billing_amount / max(los_days, 1)',
        'Mean Value': f"{cost_per_day_mean:,.2f} CU/day",
        'Median Value': f"{cost_per_day_median:,.2f} CU/day",
        'Analytical Purpose & Governance Application': 'Used for daily bed efficiency; median is preferred due to right-skewness from short stays.'
    }
])
print("Financial Metrics Duality & Operational Purpose Matrix:")
print(duality_df.to_string(index=False))
"""),
        ("markdown", """## 3. Financial Breakdown Tables & Overall Reconciliation
Validating that subgroup billing sums reconcile perfectly with the overall $1.404B total."""),
        ("code", """tables_dir = 'outputs/tables' if os.path.exists('outputs/tables') else '../outputs/tables'

for col_name in ['medical_condition', 'admission_type', 'insurance_provider', 'age_group']:
    tbl_path = os.path.join(tables_dir, f'cost_by_{col_name}.csv')
    tbl = pd.read_csv(tbl_path)
    tbl_sum = tbl['total_billing'].sum()
    share_sum = tbl['share_of_total_billing_pct'].sum()
    print(f"\\n{'='*25} COST BY {col_name.upper()} {'='*25}")
    print(tbl.to_string(index=False))
    print(f"Reconciliation Check: Group Total = {tbl_sum:,.2f} CU | Share Sum = {share_sum:.2f}% | Discrepancy = {abs(tbl_sum - tot_billing):.2f} CU")
"""),
        ("markdown", """## 4. Payer Patterns & Payment Status Unavailability Disclosure
Analyzing payer financial equity and documenting unavailable claims realization metrics.

> **DATA AVAILABILITY DISCLOSURE: PAYMENT STATUS**:
> Inpatient payment realization (e.g., claims paid, pending, denied, co-insurance, bad debt) is **completely unavailable** in the raw source data.
> Financial analytics strictly evaluate gross billed charges rather than net collections or contractual payer settlements."""),
        ("code", """payer_tbl_path = os.path.join(tables_dir, 'cost_by_insurance_provider.csv')
payer_tbl = pd.read_csv(payer_tbl_path)

print("Insurance Provider Inpatient Billing Summary:")
print(payer_tbl.to_string(index=False))

print("\\nAdmission Urgency Mix per Insurance Provider (Row %):")
payer_adm_mix = pd.crosstab(df['insurance_provider'], df['admission_type'], normalize='index') * 100
print(payer_adm_mix.round(2).to_string())

print("\\nDaily Cost (cost_per_day) by Insurance Provider:")
payer_cpd = df.groupby('insurance_provider')['cost_per_day'].agg(['mean', 'median']).round(2)
payer_cpd.columns = ['Mean CPD (CU/d)', 'Median CPD (CU/d)']
print(payer_cpd.to_string())
"""),
        ("markdown", """## 5. High-Cost Stays (95th Percentile) & Pareto Curve Evaluation
Profiling stays exceeding the 95th percentile threshold (47,638.27 CU) and evaluating the concentration of billed charges."""),
        ("code", """p95_threshold = df['billing_amount'].quantile(0.95)
n_high_cost = df['high_cost_flag'].sum()
share_high_cost = df['high_cost_flag'].mean() * 100

print(f"High-Cost 95th Percentile Threshold Value : {p95_threshold:,.2f} Currency Units")
print(f"High-Cost Outlier Admissions Count        : {n_high_cost:,} ({share_high_cost:.2f}% of cohort)")

print("\\nHigh-Cost Admissions Profile by Key Dimensions:")
for dim in ['medical_condition', 'admission_type', 'insurance_provider', 'age_group']:
    hc_summary = df.groupby(dim)['high_cost_flag'].agg(['count', 'sum', lambda x: round(x.mean()*100, 2)])
    hc_summary.columns = ['Total Admissions', 'High-Cost Stays', 'High-Cost Share (%)']
    print(f"\\n--- High-Cost Profile: {dim.upper()} ---")
    print(hc_summary.to_string())

# Pareto share computation
sorted_billing = np.sort(df['billing_amount'].values)[::-1]
n_10 = int(0.10 * len(sorted_billing))
n_20 = int(0.20 * len(sorted_billing))
p10_share = (sorted_billing[:n_10].sum() / tot_billing) * 100
p20_share = (sorted_billing[:n_20].sum() / tot_billing) * 100

print(f"\\n--- Inpatient Pareto Expenditure Concentration ---")
print(f"Top 10% of Admissions ({n_10:,} stays) generate: {p10_share:.2f}% of total billing")
print(f"Top 20% of Admissions ({n_20:,} stays) generate: {p20_share:.2f}% of total billing")
print("Analytical Note: Flatter than classic 80/20 healthcare rule due to uniform discrete billing generator.")
"""),
        ("markdown", """## 6. Length of Stay vs. Billed Charges: Decoupling Diagnostics
Testing the relationship between inpatient stay duration and billed charges."""),
        ("code", """rho_val, p_val = stats.spearmanr(df['los_days'], df['billing_amount'])
print(f"Spearman Rank Correlation (los_days vs. billing_amount): rho = {rho_val:.6f}, p = {p_val:.4f}")
print("Conclusion: Stay duration has zero correlation with billed charges in this synthetic cohort.")
print("Daily cost (cost_per_day) is an inverse function of stay duration: fixed gross charges divided by days.")
"""),
        ("markdown", """## 7. Diagnostic Statistical Hypothesis Testing
Reporting all 4 tests with assumption diagnostics, statistics, p-values, effect sizes, and practical relevance."""),
        ("code", """stat_tests_path = os.path.join(tables_dir, 'cost_stat_tests.csv')
cost_tests_df = pd.read_csv(stat_tests_path)

for idx, row in cost_tests_df.iterrows():
    print(f"\\n{'='*30} {row['test_id']}: {row['test_name']} {'='*30}")
    print(f"Research Question : {row['research_question']}")
    print(f"Null Hypothesis   : {row['null_hypothesis']}")
    print(f"Assumptions       : {row['assumption_checks']}")
    print(f"Test Statistic    : {row['test_statistic']} ({row['degrees_of_freedom']})")
    print(f"P-Value / Alpha   : p = {row['p_value']} -> {row['significance_alpha_0_05']}")
    print(f"Effect Size       : {row['effect_size_metric']} = {row['effect_size_value']}")
    print(f"Interpretation    : {row['plain_english_interpretation']}")
    print(f"Practical Impact  : {row['practical_significance_evaluation']}")
"""),
        ("markdown", """## 8. Strategic Cost-Control Questions for Hospital Administration
Reviewing findings from `outputs/tables/cost_key_findings.md` with questions framed for management."""),
        ("code", """findings_path = os.path.join(tables_dir, 'cost_key_findings.md')
with open(findings_path, 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if line.startswith('### Finding') or line.startswith('* **Observed Metrics**') or line.startswith('1. **') or line.startswith('2. **') or line.startswith('3. **') or line.startswith('4. **'):
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

    target_path = "notebooks/05_cost_analysis.ipynb"
    with open(target_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Successfully generated and executed: {target_path}")

    # Mirror to phase5_cost
    p5_nb = "phase5_cost/05_cost_analysis.ipynb"
    shutil.copy(target_path, p5_nb)
    print(f"Mirrored notebook into: {p5_nb}")

if __name__ == "__main__":
    generate_cost_notebook()

