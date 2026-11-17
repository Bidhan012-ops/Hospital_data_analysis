import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

print("--- TESTING APP.PY LOGIC STEP BY STEP ---")

# 1. Load data
file_path = os.path.join("data", "processed", "hospital_clean.csv")
assert os.path.exists(file_path), "File does not exist"
df_default = pd.read_csv(file_path)
df_default["admission_date"] = pd.to_datetime(df_default["admission_date"])
df_default["discharge_date"] = pd.to_datetime(df_default["discharge_date"])
filtered_df = df_default.copy()
print("Data loaded:", filtered_df.shape)

# 2. Test Tab 1: Overview
print("Testing Tab 1: Overview...")
monthly = filtered_df.groupby("admission_month").size().reset_index(name="admissions")
monthly["rolling_3m"] = monthly["admissions"].rolling(window=3, min_periods=1).mean()
fig_m = go.Figure()
fig_m.add_trace(go.Bar(x=monthly["admission_month"], y=monthly["admissions"]))
fig_m.add_trace(go.Scatter(x=monthly["admission_month"], y=monthly["rolling_3m"]))

urg_df = filtered_df["admission_type"].value_counts().reset_index()
urg_df.columns = ["Urgency", "Count"]
fig_u = px.pie(urg_df, values="Count", names="Urgency", hole=0.55)

weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
wk_df = filtered_df["admission_weekday"].value_counts().reindex(weekday_order).reset_index()
wk_df.columns = ["Day", "Count"]
fig_wk = px.bar(wk_df, x="Day", y="Count")

adm_c = filtered_df.groupby("admission_month").size().rename("Admissions")
dis_c = filtered_df.groupby("discharge_month").size().rename("Discharges")
flow = pd.concat([adm_c, dis_c], axis=1).fillna(0).reset_index()
flow.rename(columns={"index": "Month"}, inplace=True)
fig_f = go.Figure()
fig_f.add_trace(go.Scatter(x=flow["Month"], y=flow["Admissions"]))
print("Tab 1: PASS")

# 3. Test Tab 2: Demographics
print("Testing Tab 2: Demographics...")
fig_age = px.histogram(filtered_df, x="age", nbins=30)
fig_age.add_vline(x=filtered_df["age"].median())

age_order = ["0-17", "18-34", "35-49", "50-64", "65+"]
g_df = filtered_df.groupby(["age_group", "gender"]).size().reset_index(name="Count")
fig_g = px.bar(g_df, x="age_group", y="Count", color="gender", barmode="group", category_orders={"age_group": age_order})

b_df = filtered_df["blood_type"].value_counts().reset_index()
b_df.columns = ["Blood_Type", "Count"]
fig_b = px.bar(b_df, x="Blood_Type", y="Count")

cross_adm = pd.crosstab(filtered_df["age_group"], filtered_df["admission_type"], normalize="index") * 100
cross_adm = cross_adm.reindex(age_order)
fig_h = px.imshow(cross_adm, labels=dict(x="Urgency", y="Age Bracket", color="Share (%)"))
print("Tab 2: PASS")

# 4. Test Tab 3: Clinical
print("Testing Tab 3: Clinical...")
c_df = filtered_df["medical_condition"].value_counts().reset_index()
c_df.columns = ["Condition", "Count"]
fig_c = px.bar(c_df, x="Count", y="Condition", orientation="h")

t_cross = pd.crosstab(filtered_df["medical_condition"], filtered_df["test_results"], normalize="index") * 100
t_cross = t_cross.reset_index().melt(id_vars="medical_condition", var_name="Test_Result", value_name="Share")
fig_t = px.bar(t_cross, x="medical_condition", y="Share", color="Test_Result")

med_c = filtered_df["medication"].value_counts().reset_index()
med_c.columns = ["Medication", "Count"]
fig_med = px.bar(med_c, x="Medication", y="Count")

los_c = filtered_df.groupby("medical_condition")["los_days"].mean().reset_index()
los_c.columns = ["Condition", "ALOS"]
fig_lc = px.bar(los_c, x="Condition", y="ALOS")
print("Tab 3: PASS")

# 5. Test Tab 4: Cost & Readmissions
print("Testing Tab 4: Cost & Readmissions...")
p_df = (filtered_df.groupby("insurance_provider")["billing_amount"].sum() / 1e6).reset_index()
p_df.columns = ["Payer", "Total_Billing_M"]
fig_p = px.bar(p_df, x="Payer", y="Total_Billing_M")

sample_df = filtered_df.sample(n=min(len(filtered_df), 3000), random_state=42)
fig_sc = px.scatter(sample_df, x="los_days", y="billing_amount", color="admission_type")

elig_df = filtered_df[filtered_df["readmission_eligible"] == 1]
r_type = elig_df.groupby("admission_type").agg(Eligible=("admission_id", "count"), Readmissions=("readmitted_30d", "sum")).reset_index()
r_type["Rate_Pct"] = (r_type["Readmissions"] / r_type["Eligible"]) * 100
fig_r = px.bar(r_type, x="admission_type", y="Rate_Pct", color="admission_type")

readm_c = filtered_df[filtered_df["readmitted_30d"] == 1]
fig_tim = px.histogram(readm_c, x="days_to_next_admission", nbins=15)
print("Tab 4: PASS")

# 6. Test Tab 5: Data Explorer
print("Testing Tab 5: Data Explorer...")
preview_cols = [
    "admission_id", "patient_key", "doctor_id", "age", "age_group",
    "gender", "blood_type", "medical_condition", "admission_type",
    "admission_date", "discharge_date", "los_days", "insurance_provider",
    "billing_amount", "cost_per_day", "readmitted_30d"
]
disp_df = filtered_df[preview_cols]
csv_bytes = filtered_df[preview_cols].to_csv(index=False).encode("utf-8")
assert len(csv_bytes) > 0
print("Tab 5: PASS")

# 7. Test Power BI View tables
print("Testing Power BI files...")
tables = [
    "Fact_Admissions.csv", "Dim_Date.csv", "Dim_Patient.csv",
    "Dim_Doctor.csv", "Dim_Hospital.csv", "Dim_Condition.csv"
]
for t in tables:
    p = os.path.join("powerbi", t)
    assert os.path.exists(p)
    with open(p, "rb") as f:
        data = f.read()
    assert len(data) > 0
print("Power BI files: PASS")

print("\n--- ALL TESTS PASSED SUCCESSFULLY! ---")
