import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

df = pd.read_csv("data/processed/hospital_clean.csv")

# 1. Billing Overview
s = df["billing_amount"]
tot = s.sum()
mean_b = s.mean()
med_b = s.median()
std_b = s.std()
skew_b = s.skew()
p5, p25, p50, p75, p95, p99 = np.percentile(s, [5, 25, 50, 75, 95, 99])
print("=== BILLING STATS ===")
print(f"Total: {tot:,.2f}")
print(f"Mean: {mean_b:,.2f}, Median: {med_b:,.2f}, Std: {std_b:,.2f}, Skewness: {skew_b:.4f}")
print(f"P5={p5:,.2f}, P25={p25:,.2f}, P50={p50:,.2f}, P75={p75:,.2f}, P95={p95:,.2f}, P99={p99:,.2f}")

# Negative & Zero billing
neg_count = (s < 0).sum()
zero_count = (s == 0).sum()
print(f"Negative billing: {neg_count} records (Min: {s.min():,.2f})")
print(f"Zero billing: {zero_count} records")

# 2. Cost definitions
n_adm = len(df)
n_pat = df["patient_key"].nunique()
cost_per_admission = tot / n_adm
cost_per_patient = tot / n_pat
mean_cost_per_day = df["cost_per_day"].mean()
med_cost_per_day = df["cost_per_day"].median()
print(f"\nCost per admission (Mean): {cost_per_admission:,.2f}")
print(f"Cost per patient: {cost_per_patient:,.2f} across {n_pat:,} unique patients")
print(f"Cost per day (Mean): {mean_cost_per_day:,.2f}, Median: {med_cost_per_day:,.2f}")

# 3. High cost threshold
p95 = s.quantile(0.95)
print(f"\nHigh cost threshold (95th percentile): {p95:,.2f}")
print(f"High cost count: {df['high_cost_flag'].sum():,} ({df['high_cost_flag'].mean()*100:.2f}%)")

# 4. Pareto calculations (Top 10% and Top 20% billing share)
sorted_b = df["billing_amount"].sort_values(ascending=False).values
n_10 = int(0.10 * len(sorted_b))
n_20 = int(0.20 * len(sorted_b))
share_top10 = (sorted_b[:n_10].sum() / tot) * 100
share_top20 = (sorted_b[:n_20].sum() / tot) * 100
print(f"Pareto Share of Total Billing:")
print(f"  Top 10% admissions ({n_10:,} stays) generate: {share_top10:.2f}% of total billing")
print(f"  Top 20% admissions ({n_20:,} stays) generate: {share_top20:.2f}% of total billing")

# 5. Statistical Tests
# Test 1: Kruskal-Wallis across Insurance Provider
groups_ins = [g["billing_amount"].values for _, g in df.groupby("insurance_provider")]
h_ins, p_ins = stats.kruskal(*groups_ins)
eta2_ins = (h_ins - len(groups_ins) + 1) / (len(df) - len(groups_ins))
print(f"\nTest 1 (Billing across Payer): H = {h_ins:.4f}, p = {p_ins:.4f}, eta2 = {eta2_ins:.6f}")

# Test 2: Kruskal-Wallis across Medical Condition + pairwise Holm
groups_cond = [g["billing_amount"].values for _, g in df.groupby("medical_condition")]
h_cond, p_cond = stats.kruskal(*groups_cond)
eta2_cond = (h_cond - len(groups_cond) + 1) / (len(df) - len(groups_cond))
print(f"Test 2 (Billing across Condition): H = {h_cond:.4f}, p = {p_cond:.4f}, eta2 = {eta2_cond:.6f}")

# Pairwise Mann-Whitney with Holm for largest differences
cond_means = df.groupby("medical_condition")["billing_amount"].mean().sort_values()
print("Condition Mean Billing:\n", cond_means)
# Test max vs min condition:
c_max, c_min = cond_means.index[-1], cond_means.index[0]
u_pair, p_pair = stats.mannwhitneyu(df[df["medical_condition"] == c_max]["billing_amount"],
                                    df[df["medical_condition"] == c_min]["billing_amount"])
print(f"Pairwise Mann-Whitney ({c_max} vs {c_min}): U = {u_pair:.1f}, p = {p_pair:.4f}")

# Test 3: Spearman correlation between LOS and Billing Amount
rho_lb, p_lb = stats.spearmanr(df["los_days"], df["billing_amount"])
z_lb = np.arctanh(rho_lb)
se_z = 1.0 / np.sqrt(len(df) - 3)
ci_low_lb = np.tanh(z_lb - 1.96 * se_z)
ci_high_lb = np.tanh(z_lb + 1.96 * se_z)
print(f"Test 3 (Spearman LOS vs Billing): rho = {rho_lb:.6f}, p = {p_lb:.4f}, 95% CI = [{ci_low_lb:.4f}, {ci_high_lb:.4f}]")

# Test 4: Chi-Square of high_cost_flag vs admission_type
ct_adm_hc = pd.crosstab(df["admission_type"], df["high_cost_flag"])
chi2_adm_hc, p_adm_hc, dof_adm_hc, _ = stats.chi2_contingency(ct_adm_hc)
v_adm_hc = np.sqrt(chi2_adm_hc / (len(df) * (min(ct_adm_hc.shape) - 1)))
print(f"Test 4 (High Cost vs Admission Type): Chi2 = {chi2_adm_hc:.4f}, p = {p_adm_hc:.4f}, Cramers V = {v_adm_hc:.6f}")

# Bootstrap 95% CI for mean billing per provider (2000 resamples, seed 42)
rng = np.random.default_rng(42)
print("\nBootstrap 95% CIs for Mean Billing per Provider:")
for p, g in df.groupby("insurance_provider"):
    vals = g["billing_amount"].values
    n = len(vals)
    boot_means = [rng.choice(vals, size=n, replace=True).mean() for _ in range(2000)]
    ci_l = np.percentile(boot_means, 2.5)
    ci_u = np.percentile(boot_means, 97.5)
    print(f"  {p}: Mean = {vals.mean():,.2f}, 95% CI = [{ci_l:,.2f}, {ci_u:,.2f}]")

