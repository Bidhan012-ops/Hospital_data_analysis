import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

df = pd.read_csv("data/processed/hospital_clean.csv")

# 1. Recompute los_days and assert
recomputed_los = (pd.to_datetime(df["discharge_date"]) - pd.to_datetime(df["admission_date"])).dt.days
assert (recomputed_los == df["los_days"]).all(), "Recomputed los_days does not match existing los_days!"
print("Assertion Passed: recomputed los_days strictly matches canonical los_days across all 54,966 records.")

# 2. Overall stats
s = df["los_days"]
q1, q3 = s.quantile(0.25), s.quantile(0.75)
print(f"Overall ALOS: Mean={s.mean():.2f}, Median={s.median():.1f}, IQR={q3-q1:.1f}, Std={s.std():.2f}, Min={s.min()}, Max={s.max()}, Skewness={s.skew():.4f}")

# 3. Normality test (D'Agostino-Pearson) on sample of 5,000
sample_los = df["los_days"].sample(5000, random_state=42)
k2, p_dag = stats.normaltest(sample_los)
print(f"D'Agostino normality test (N=5000): K2 = {k2:.4f}, p = {p_dag:.4e}")

# 4. Levene tests
lev_adm, p_lev_adm = stats.levene(*[g["los_days"].values for _, g in df.groupby("admission_type")])
print(f"Levene Test across Admission Type: W = {lev_adm:.4f}, p = {p_lev_adm:.4f}")

lev_cond, p_lev_cond = stats.levene(*[g["los_days"].values for _, g in df.groupby("medical_condition")])
print(f"Levene Test across Medical Condition: W = {lev_cond:.4f}, p = {p_lev_cond:.4f}")

# 5. Kruskal-Wallis across admission_type
groups_adm = [g["los_days"].values for _, g in df.groupby("admission_type")]
h_adm, p_h_adm = stats.kruskal(*groups_adm)
k_adm = len(groups_adm)
n_tot = len(df)
eta2_adm = (h_adm - k_adm + 1) / (n_tot - k_adm)
eps2_adm = h_adm / ((n_tot**2 - 1) / (n_tot + 1))
print(f"Kruskal-Wallis across Admission Type: H = {h_adm:.4f}, p = {p_h_adm:.4e}, eta2 = {eta2_adm:.6f}, eps2 = {eps2_adm:.6f}")

# 6. Kruskal-Wallis across medical_condition & pairwise Mann-Whitney with Holm
groups_cond = [g["los_days"].values for _, g in df.groupby("medical_condition")]
h_cond, p_h_cond = stats.kruskal(*groups_cond)
k_cond = len(groups_cond)
eta2_cond = (h_cond - k_cond + 1) / (n_tot - k_cond)
print(f"Kruskal-Wallis across Medical Condition: H = {h_cond:.4f}, p = {p_h_cond:.4e}, eta2 = {eta2_cond:.6f}")

# Pairwise Mann-Whitney with Holm
conds = sorted(df["medical_condition"].unique())
pairs = []
p_vals = []
u_stats = []
for i in range(len(conds)):
    for j in range(i + 1, len(conds)):
        c1, c2 = conds[i], conds[j]
        v1 = df[df["medical_condition"] == c1]["los_days"]
        v2 = df[df["medical_condition"] == c2]["los_days"]
        u, p = stats.mannwhitneyu(v1, v2, alternative="two-sided")
        pairs.append(f"{c1} vs {c2}")
        p_vals.append(p)
        u_stats.append(u)

reject, p_adj, _, _ = multipletests(p_vals, alpha=0.05, method="holm")
print("Pairwise Mann-Whitney tests (Holm-corrected):")
for pair, u, p_orig, p_corr, rej in zip(pairs[:5], u_stats[:5], p_vals[:5], p_adj[:5], reject[:5]):
    print(f"  {pair}: U={u:.1f}, p_orig={p_orig:.4f}, p_holm={p_corr:.4f}, reject={rej}")

# 7. Mann-Whitney U for Gender
males = df[df["gender"] == "Male"]["los_days"]
females = df[df["gender"] == "Female"]["los_days"]
u_gen, p_gen = stats.mannwhitneyu(males, females, alternative="two-sided")
n1, n2 = len(males), len(females)
# Rank-biserial correlation: r_rb = 1 - (2*U) / (n1 * n2)
r_rb = 1.0 - (2.0 * u_gen) / (n1 * n2)
print(f"Mann-Whitney U by Gender: U = {u_gen:.1f}, p = {p_gen:.4f}, rank-biserial r = {r_rb:.6f}")

# 8. Spearman correlation of age and los_days
rho, p_rho = stats.spearmanr(df["age"], df["los_days"])
# Fisher z-transformation for 95% CI of Spearman rho
z_rho = np.arctanh(rho)
se_z = 1.0 / np.sqrt(n_tot - 3)
ci_low_z = z_rho - 1.96 * se_z
ci_high_z = z_rho + 1.96 * se_z
ci_low_rho = np.tanh(ci_low_z)
ci_high_rho = np.tanh(ci_high_z)
print(f"Spearman correlation (Age vs LOS): rho = {rho:.6f}, p = {p_rho:.4f}, 95% CI = [{ci_low_rho:.4f}, {ci_high_rho:.4f}]")

