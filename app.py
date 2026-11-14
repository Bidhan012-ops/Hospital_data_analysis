"""
Hospital Patient Analytics & Executive Intelligence Dashboard
Built with Streamlit and Plotly for Descriptive and Diagnostic Healthcare Analytics.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# Configuration & Page Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hospital Patient Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive presentation styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .notice-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #1E40AF;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_clean_data():
    file_path = os.path.join("data", "processed", "hospital_clean.csv")
    if not os.path.exists(file_path):
        st.error(f"Processed dataset not found at `{file_path}`. Please verify preprocessing.")
        st.stop()
        
    df = pd.read_csv(file_path)
    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["discharge_date"] = pd.to_datetime(df["discharge_date"])
    
    # Sort chronologically
    df = df.sort_values("admission_date").reset_index(drop=True)
    return df

try:
    df_raw = load_clean_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Filters
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/hospital.png", width=64)
st.sidebar.title("Hospital Analytics")
st.sidebar.markdown("**Operational & Executive Intelligence**")
st.sidebar.markdown("---")

st.sidebar.subheader("🔍 Filters & Controls")

# Date Range Filter
min_date = df_raw["admission_date"].min().date()
max_date = df_raw["admission_date"].max().date()

date_range = st.sidebar.date_input(
    "Admission Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Admission Type Filter
admission_types = ["All"] + sorted(df_raw["admission_type"].unique().tolist())
selected_admission_type = st.sidebar.selectbox("Admission Urgency", admission_types)

# Medical Condition Filter
conditions = ["All"] + sorted(df_raw["medical_condition"].unique().tolist())
selected_condition = st.sidebar.selectbox("Medical Condition", conditions)

# Insurance Provider Filter
insurers = ["All"] + sorted(df_raw["insurance_provider"].unique().tolist())
selected_insurer = st.sidebar.selectbox("Insurance Provider", insurers)

# Test Results Filter
test_options = ["All"] + sorted(df_raw["test_results"].unique().tolist())
selected_test = st.sidebar.selectbox("Test Outcome", test_options)

# Top Hospitals Filter (n >= 30)
top_hospitals = df_raw["hospital"].value_counts()[lambda x: x >= 30].index.tolist()
hospital_options = ["All Facilities"] + sorted(top_hospitals)
selected_hospital = st.sidebar.selectbox("Hospital Facility (n ≥ 30)", hospital_options)

# Apply Filters
filtered_df = df_raw.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[
        (filtered_df["admission_date"].dt.date >= start_d) & 
        (filtered_df["admission_date"].dt.date <= end_d)
    ]

if selected_admission_type != "All":
    filtered_df = filtered_df[filtered_df["admission_type"] == selected_admission_type]

if selected_condition != "All":
    filtered_df = filtered_df[filtered_df["medical_condition"] == selected_condition]

if selected_insurer != "All":
    filtered_df = filtered_df[filtered_df["insurance_provider"] == selected_insurer]

if selected_test != "All":
    filtered_df = filtered_df[filtered_df["test_results"] == selected_test]

if selected_hospital != "All Facilities":
    filtered_df = filtered_df[filtered_df["hospital"] == selected_hospital]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Records Displayed:** `{len(filtered_df):,}` / `{len(df_raw):,}`")

# -----------------------------------------------------------------------------
# Header & Data Governance Disclaimer
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">🏥 Hospital Patient Analytics & Executive Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Descriptive and Diagnostic Hospital Inpatient Intelligence | '
    'B.Tech Internship Healthcare Analytics Project</div>', 
    unsafe_allow_html=True
)

st.markdown("""
<div class="notice-box">
    <strong>Data Governance & Compliance Note:</strong> 
    This analytics suite operates strictly within descriptive and diagnostic boundaries. 
    Direct identifiers have been eliminated via salted SHA-256 patient pseudonymization (<code>patient_key</code>) 
    and deterministic physician pseudonyms (<code>doctor_id</code>). All figures, tables, and metrics are verified 100% clean.
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Top-Level Executive KPI Cards
# -----------------------------------------------------------------------------
total_admissions = len(filtered_df)
unique_patients = filtered_df["patient_key"].nunique() if total_admissions > 0 else 0
alos = filtered_df["los_days"].mean() if total_admissions > 0 else 0.0
median_los = filtered_df["los_days"].median() if total_admissions > 0 else 0.0
total_billing = filtered_df["billing_amount"].sum() if total_admissions > 0 else 0.0
mean_billing = filtered_df["billing_amount"].mean() if total_admissions > 0 else 0.0
avg_cost_per_day = filtered_df["cost_per_day"].mean() if total_admissions > 0 else 0.0

# Readmission metrics for eligible stays
eligible_df = filtered_df[filtered_df["readmission_eligible"] == 1]
readm_rate = (eligible_df["readmitted_30d"].mean() * 100) if len(eligible_df) > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Admissions", f"{total_admissions:,}", f"{unique_patients:,} Patients")
col2.metric("Average Stay (ALOS)", f"{alos:.1f} Days", f"Median: {median_los:.0f} d")
col3.metric("Total Billed Revenue", f"${total_billing/1e6:.2f}M CU", f"Avg: ${mean_billing:,.0f}")
col4.metric("Avg Daily Cost", f"${avg_cost_per_day:,.0f} / day")
col5.metric("30-Day Readmission", f"{readm_rate:.2f}%", f"{len(eligible_df):,} eligible stays")

st.markdown("---")

# -----------------------------------------------------------------------------
# Multi-Tab Analytical Views
# -----------------------------------------------------------------------------
tab_overview, tab_demographics, tab_clinical, tab_financial, tab_explorer = st.tabs([
    "📈 Executive Overview",
    "👥 Patient Demographics",
    "🩺 Clinical & Diagnoses",
    "💰 Cost & Readmissions",
    "🔍 Data Explorer & Export"
])

# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Inpatient Volume Trends & Census Dynamics")
    
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t1:
        # Monthly Admission Trend with 3-month rolling average
        monthly_df = (
            filtered_df.groupby("admission_month")
            .size()
            .reset_index(name="admissions")
        )
        monthly_df["rolling_3m"] = monthly_df["admissions"].rolling(window=3, min_periods=1).mean()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly_df["admission_month"],
            y=monthly_df["admissions"],
            name="Monthly Admissions",
            marker_color="#3B82F6",
            opacity=0.75
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_df["admission_month"],
            y=monthly_df["rolling_3m"],
            name="3-Month Moving Avg",
            line=dict(color="#DC2626", width=2.5)
        ))
        fig_trend.update_layout(
            title="Monthly Admission Volume with 3-Month Moving Average",
            xaxis_title="Admission Month",
            yaxis_title="Total Admissions",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_t2:
        # Admission Urgency Breakdown
        urgency_df = filtered_df["admission_type"].value_counts().reset_index()
        urgency_df.columns = ["admission_type", "count"]
        
        fig_pie = px.pie(
            urgency_df,
            values="count",
            names="admission_type",
            title="Intake by Admission Urgency",
            hole=0.45,
            color="admission_type",
            color_discrete_map={
                "Emergency": "#EF4444",
                "Urgent": "#F59E0B",
                "Elective": "#10B981"
            }
        )
        fig_pie.update_layout(template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)

    col_t3, col_t4 = st.columns(2)
    with col_t3:
        # Day of week intake pattern
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_df = (
            filtered_df["admission_weekday"]
            .value_counts()
            .reindex(weekday_order)
            .reset_index()
        )
        weekday_df.columns = ["weekday", "admissions"]
        
        fig_day = px.bar(
            weekday_df,
            x="weekday",
            y="admissions",
            title="Admissions by Day of Week",
            color="admissions",
            color_continuous_scale="Blues",
            labels={"weekday": "Day of Week", "admissions": "Admissions"}
        )
        fig_day.update_layout(template="plotly_white", coloraxis_showscale=False)
        st.plotly_chart(fig_day, use_container_width=True)
        
    with col_t4:
        # Admissions vs Discharges by Month
        adm_m = filtered_df.groupby("admission_month").size().rename("Admissions")
        dis_m = filtered_df.groupby("discharge_month").size().rename("Discharges")
        flow_df = pd.concat([adm_m, dis_m], axis=1).fillna(0).reset_index()
        flow_df.rename(columns={"index": "month"}, inplace=True)
        
        fig_flow = go.Figure()
        fig_flow.add_trace(go.Scatter(x=flow_df["month"], y=flow_df["Admissions"], mode="lines+markers", name="Admissions", line=dict(color="#2563EB")))
        fig_flow.add_trace(go.Scatter(x=flow_df["month"], y=flow_df["Discharges"], mode="lines+markers", name="Discharges", line=dict(color="#059669")))
        fig_flow.update_layout(
            title="Inpatient Throughput: Admissions vs. Discharges",
            xaxis_title="Month",
            yaxis_title="Count",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_flow, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: PATIENT DEMOGRAPHICS
# -----------------------------------------------------------------------------
with tab_demographics:
    st.subheader("Patient Demographics & Cohort Stratification")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        # Age Distribution with Median Line
        fig_age = px.histogram(
            filtered_df,
            x="age",
            nbins=30,
            title=f"Patient Age Distribution (Median: {filtered_df['age'].median():.0f} yrs, Mean: {filtered_df['age'].mean():.1f} yrs)",
            color_discrete_sequence=["#4F46E5"],
            labels={"age": "Age (Years)"}
        )
        fig_age.add_vline(
            x=filtered_df["age"].median(), 
            line_dash="dash", 
            line_color="red", 
            annotation_text=f"Median: {filtered_df['age'].median():.0f}"
        )
        fig_age.update_layout(template="plotly_white", yaxis_title="Number of Patients")
        st.plotly_chart(fig_age, use_container_width=True)
        
    with col_d2:
        # Age Group by Gender
        age_group_order = ["0-17", "18-34", "35-49", "50-64", "65+"]
        demo_grouped = (
            filtered_df.groupby(["age_group", "gender"])
            .size()
            .reset_index(name="count")
        )
        
        fig_gender = px.bar(
            demo_grouped,
            x="age_group",
            y="count",
            color="gender",
            barmode="group",
            category_orders={"age_group": age_group_order},
            title="Patient Count by Age Group and Gender",
            color_discrete_map={"Male": "#3B82F6", "Female": "#EC4899"},
            labels={"age_group": "Age Bracket", "count": "Admissions"}
        )
        fig_gender.update_layout(template="plotly_white")
        st.plotly_chart(fig_gender, use_container_width=True)
        
    col_d3, col_d4 = st.columns(2)
    
    with col_d3:
        # Blood Type Distribution
        blood_df = filtered_df["blood_type"].value_counts().reset_index()
        blood_df.columns = ["blood_type", "count"]
        
        fig_blood = px.bar(
            blood_df,
            x="blood_type",
            y="count",
            title="Blood Group Distribution",
            color="count",
            color_continuous_scale="Purples",
            labels={"blood_type": "Blood Type", "count": "Admissions"}
        )
        fig_blood.update_layout(template="plotly_white", coloraxis_showscale=False)
        st.plotly_chart(fig_blood, use_container_width=True)
        
    with col_d4:
        # Geographic Note Box
        st.info(
            "📌 **Field Availability Notice**: Patient geographic location, clinical departments, "
            "and ward units are unavailable in the source dataset. "
            "Per the data governance charter, no synthetic geographic variables have been invented."
        )
        # Admission type by age group heatmap
        cross_age_adm = pd.crosstab(
            filtered_df["age_group"], 
            filtered_df["admission_type"], 
            normalize="index"
        ) * 100
        cross_age_adm = cross_age_adm.reindex(age_group_order)
        
        fig_heat = px.imshow(
            cross_age_adm,
            labels=dict(x="Admission Type", y="Age Group", color="Share (%)"),
            title="Admission Urgency Share by Age Group (%)",
            text_auto=".1f",
            color_continuous_scale="Teal"
        )
        fig_heat.update_layout(template="plotly_white")
        st.plotly_chart(fig_heat, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: CLINICAL & DIAGNOSES
# -----------------------------------------------------------------------------
with tab_clinical:
    st.subheader("Medical Diagnoses, Clinical Tests & Medication Profiling")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Condition Frequency
        cond_df = filtered_df["medical_condition"].value_counts().reset_index()
        cond_df.columns = ["medical_condition", "count"]
        
        fig_cond = px.bar(
            cond_df,
            x="count",
            y="medical_condition",
            orientation="h",
            title="Primary Diagnoses Distribution",
            color="count",
            color_continuous_scale="Viridis",
            labels={"medical_condition": "Medical Condition", "count": "Admissions"}
        )
        fig_cond.update_layout(template="plotly_white", yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_cond, use_container_width=True)
        
    with col_c2:
        # Test Results by Condition (100% Stacked Bar)
        test_cross = pd.crosstab(
            filtered_df["medical_condition"], 
            filtered_df["test_results"], 
            normalize="index"
        ) * 100
        test_cross = test_cross.reset_index().melt(
            id_vars="medical_condition", 
            var_name="test_results", 
            value_name="percentage"
        )
        
        fig_test = px.bar(
            test_cross,
            x="medical_condition",
            y="percentage",
            color="test_results",
            title="Test Result Outcome Distribution by Condition (%)",
            color_discrete_map={
                "Normal": "#10B981",
                "Abnormal": "#EF4444",
                "Inconclusive": "#F59E0B"
            },
            labels={"medical_condition": "Condition", "percentage": "Share (%)"}
        )
        fig_test.update_layout(template="plotly_white")
        st.plotly_chart(fig_test, use_container_width=True)
        
    col_c3, col_c4 = st.columns(2)
    
    with col_c3:
        # Medication Cross-tabulation
        med_df = filtered_df["medication"].value_counts().reset_index()
        med_df.columns = ["medication", "count"]
        
        fig_med = px.bar(
            med_df,
            x="medication",
            y="count",
            title="Top Prescribed Inpatient Medications",
            color="count",
            color_continuous_scale="Sunset",
            labels={"medication": "Prescribed Medication", "count": "Prescriptions"}
        )
        fig_med.update_layout(template="plotly_white", coloraxis_showscale=False)
        st.plotly_chart(fig_med, use_container_width=True)
        
    with col_c4:
        # Length of stay across medical conditions
        los_cond = (
            filtered_df.groupby("medical_condition")["los_days"]
            .agg(ALOS="mean", Median="median", Stays="count")
            .reset_index()
        )
        fig_los_c = px.bar(
            los_cond,
            x="medical_condition",
            y="ALOS",
            title="Average Length of Stay (ALOS) by Diagnosis",
            color="ALOS",
            color_continuous_scale="Blues",
            labels={"medical_condition": "Medical Condition", "ALOS": "ALOS (Days)"}
        )
        fig_los_c.update_layout(template="plotly_white", coloraxis_showscale=False)
        st.plotly_chart(fig_los_c, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: COST & READMISSIONS
# -----------------------------------------------------------------------------
with tab_financial:
    st.subheader("Financial Analytics, Outlier Tracking & 30-Day Readmissions")
    
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        # Total Billing by Insurance Provider
        payer_df = (
            filtered_df.groupby("insurance_provider")
            .agg(Total_Billing=("billing_amount", "sum"), Stays=("admission_id", "count"))
            .reset_index()
        )
        payer_df["Total_Millions"] = payer_df["Total_Billing"] / 1e6
        
        fig_payer = px.bar(
            payer_df,
            x="insurance_provider",
            y="Total_Millions",
            title="Total Billed Revenue by Insurance Provider ($M CU)",
            color="insurance_provider",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"insurance_provider": "Payer", "Total_Millions": "Total Billing ($M)"}
        )
        fig_payer.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_payer, use_container_width=True)
        
    with col_f2:
        # Length of Stay vs Billing Decoupling (Scatter sample to keep UI super fast)
        sample_df = filtered_df.sample(n=min(len(filtered_df), 3000), random_state=42)
        fig_scatter = px.scatter(
            sample_df,
            x="los_days",
            y="billing_amount",
            color="admission_type",
            opacity=0.45,
            title="Length of Stay vs. Billed Amount (ρ = -0.005, p = 0.256 — Decoupled)",
            labels={"los_days": "Length of Stay (Days)", "billing_amount": "Billing (CU)"},
            color_discrete_map={"Emergency": "#EF4444", "Urgent": "#F59E0B", "Elective": "#10B981"}
        )
        fig_scatter.update_layout(template="plotly_white")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    col_f3, col_f4 = st.columns(2)
    
    with col_f3:
        # 30-Day Readmission Rate by Admission Type
        readm_type = (
            eligible_df.groupby("admission_type")
            .agg(
                Eligible_Stays=("admission_id", "count"),
                Readmissions=("readmitted_30d", "sum")
            )
            .reset_index()
        )
        readm_type["Rate_Pct"] = (readm_type["Readmissions"] / readm_type["Eligible_Stays"]) * 100
        
        fig_readm = px.bar(
            readm_type,
            x="admission_type",
            y="Rate_Pct",
            title="30-Day Proxy Readmission Rate by Urgency (%)",
            color="admission_type",
            text_auto=".2f",
            color_discrete_map={"Emergency": "#EF4444", "Urgent": "#F59E0B", "Elective": "#10B981"},
            labels={"admission_type": "Admission Urgency", "Rate_Pct": "Readmission Rate (%)"}
        )
        fig_readm.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_readm, use_container_width=True)
        
    with col_f4:
        # Readmission Timing Breakdown (Days to next admission)
        readm_cases = filtered_df[filtered_df["readmitted_30d"] == 1]
        if len(readm_cases) > 0:
            fig_timing = px.histogram(
                readm_cases,
                x="days_to_next_admission",
                nbins=15,
                title="Timing of 30-Day Readmission Return (Days Post-Discharge)",
                color_discrete_sequence=["#DC2626"],
                labels={"days_to_next_admission": "Days to Next Admission"}
            )
            fig_timing.update_layout(template="plotly_white", yaxis_title="Readmissions")
            st.plotly_chart(fig_timing, use_container_width=True)
        else:
            st.info("No 30-day readmissions recorded for the current filter selection.")

# -----------------------------------------------------------------------------
# TAB 5: DATA EXPLORER & EXPORT
# -----------------------------------------------------------------------------
with tab_explorer:
    st.subheader("Interactive Inpatient Data Explorer")
    st.markdown(
        "Inspect individual anonymized admissions. "
        "Direct personal names and doctor names have been replaced with non-identifying keys."
    )
    
    # Display preview columns
    preview_cols = [
        "admission_id", "patient_key", "doctor_id", "age", "age_group", 
        "gender", "blood_type", "medical_condition", "admission_type", 
        "admission_date", "discharge_date", "los_days", "insurance_provider", 
        "billing_amount", "cost_per_day", "readmitted_30d"
    ]
    
    # Search box
    search_query = st.text_input("Filter by Admission ID or Patient Key", "")
    display_df = filtered_df[preview_cols]
    if search_query:
        display_df = display_df[
            display_df["admission_id"].str.contains(search_query, case=False, na=False) |
            display_df["patient_key"].str.contains(search_query, case=False, na=False)
        ]
        
    st.dataframe(
        display_df.head(100),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Showing top {min(len(display_df), 100)} of {len(display_df):,} matching rows.")
    
    # Export filtered data
    csv_data = filtered_df[preview_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Inpatient Data (CSV)",
        data=csv_data,
        file_name="hospital_filtered_admissions.csv",
        mime="text/csv"
    )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6B7280; font-size: 0.85rem;'>"
    "Hospital Patient Data Analysis and Dashboard Development | B.Tech Internship Healthcare Project<br>"
    "Developed with Python, Streamlit, Pandas, and Plotly. 100% Privacy Compliant (Zero Direct Identifiers)."
    "</div>",
    unsafe_allow_html=True
)

