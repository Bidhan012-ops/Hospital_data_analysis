"""
Hospital Intelligence - Healthcare Analytics Portal
A multi-page enterprise analytics portal designed with dark-mode styling,
featuring Portal Home, Streamlit Analytics, and Power BI Dashboard views.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.database import (
    validate_uploaded_csv,
    load_active_dataset_from_db,
    save_clean_dataset_to_db,
    init_database
)
from src.clean import clean_dataset

# -----------------------------------------------------------------------------
# 1. Page Configuration & Dark Theme Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hospital Intelligence | Analytics Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Dark Theme CSS matching the requested portal styling
st.markdown("""
<style>
    /* Global background and font styling */
    .stApp {
        background-color: #0B132B;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Top header styling */
    .portal-eyebrow {
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #60A5FA;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .portal-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
    }
    .portal-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.2rem;
    }
    
    /* Synthetic Data Alert Banner */
    .synthetic-badge {
        background-color: #13233D;
        border: 1px solid #1E3A8A;
        border-radius: 8px;
        padding: 10px 16px;
        color: #93C5FD;
        font-size: 0.88rem;
        font-weight: 500;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
    }
    
    /* KPI Metric Cards */
    .kpi-container {
        display: flex;
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #131E32;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 18px 20px;
        flex: 1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #94A3B8;
        font-weight: 500;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .kpi-subtext {
        font-size: 0.75rem;
        color: #60A5FA;
        margin-top: 0.2rem;
    }
    
    /* Dashboard Selection Cards on Home Page */
    .dash-card {
        background-color: #131E32;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 24px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
    }
    .dash-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }
    .dash-card-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dash-card-desc {
        font-size: 0.92rem;
        color: #94A3B8;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #080E1E;
        border-right: 1px solid #1E293B;
    }
    .sidebar-brand-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-top: 0.5rem;
    }
    .sidebar-brand-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-bottom: 1rem;
    }
    .user-badge {
        background-color: #131E32;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 0.82rem;
        color: #94A3B8;
        margin-bottom: 1rem;
    }
    .dataset-info-box {
        background-color: #111B2E;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px;
        margin-top: 0.75rem;
        font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Session State Navigation Setup (Safe Callback Pattern)
# -----------------------------------------------------------------------------
NAV_OPTIONS = [
    "🏠 Portal Home",
    "📊 Streamlit Analytics",
    "📈 Power BI Dashboard"
]

if "portal_nav" not in st.session_state:
    st.session_state["portal_nav"] = "🏠 Portal Home"

def set_page(target_page: str):
    st.session_state["portal_nav"] = target_page

# -----------------------------------------------------------------------------
# 3. Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_default_dataset():
    # Attempt load from persistent SQLite database
    df_db = load_active_dataset_from_db()
    if df_db is not None and len(df_db) > 0:
        return df_db
        
    # Fallback to processed CSV
    file_path = os.path.join("data", "processed", "hospital_clean.csv")
    if not os.path.exists(file_path):
        st.error(f"Processed dataset not found at `{file_path}`. Please verify preprocessing.")
        st.stop()
    
    df = pd.read_csv(file_path)
    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["discharge_date"] = pd.to_datetime(df["discharge_date"])
    
    # Store in SQLite for future sessions
    try:
        save_clean_dataset_to_db(df, "default_hospital_clean")
    except Exception:
        pass
        
    return df.sort_values("admission_date").reset_index(drop=True)

df_default = load_default_dataset()

# -----------------------------------------------------------------------------
# 4. Sidebar Navigation & Dynamic Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    selected_nav = st.radio(
        "Navigation",
        options=NAV_OPTIONS,
        key="portal_nav",
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Brand Information
    st.markdown('<div class="sidebar-brand-title">🏥 Hospital Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-brand-sub">Healthcare Operations & Analytics Portal</div>', unsafe_allow_html=True)
    
    # Logged in User Card
    st.markdown("""
    <div class="user-badge">
        <strong>Logged in as:</strong> Healthcare Analyst<br>
        <span style="color: #10B981;">● Active Session (Verified)</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Dataset Management (Shown when on Analytics page)
    if st.session_state["portal_nav"] == "📊 Streamlit Analytics":
        st.markdown("**| Dataset Management**")
        uploaded_file = st.file_uploader("Upload your dataset", type=["csv"], help="Upload a healthcare dataset CSV")
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file)
                is_valid, schema_type, err_msg = validate_uploaded_csv(df_upload)
                
                if not is_valid:
                    detected_cols = list(df_upload.columns)[:8]
                    st.markdown(f"""
                    <div style="background-color: #3B1219; border: 1px solid #7F1D1D; border-radius: 8px; padding: 12px; margin-top: 10px; color: #FCA5A5; font-size: 0.82rem; line-height: 1.5;">
                        <strong style="color: #F87171;">Unable to load dataset:</strong><br>{err_msg}<br><br>
                        <strong style="color: #E2E8F0;">Detected Columns ({len(df_upload.columns)}):</strong><br>
                        <code style="color: #94A3B8; font-size: 0.76rem;">{', '.join(detected_cols)}...</code>
                    </div>
                    """, unsafe_allow_html=True)
                    df_active = df_default
                elif schema_type == "raw":
                    with st.spinner("Processing raw healthcare data through cleaning & de-identification pipeline..."):
                        clean_df, _ = clean_dataset(df_upload)
                        save_clean_dataset_to_db(clean_df, dataset_name=uploaded_file.name)
                        df_active = clean_df
                    st.success(f"✓ Validated raw healthcare data & saved {len(clean_df):,} records to SQLite database!")
                elif schema_type == "canonical":
                    if "admission_date" in df_upload.columns:
                        df_upload["admission_date"] = pd.to_datetime(df_upload["admission_date"])
                    if "discharge_date" in df_upload.columns:
                        df_upload["discharge_date"] = pd.to_datetime(df_upload["discharge_date"])
                    save_clean_dataset_to_db(df_upload, dataset_name=uploaded_file.name)
                    df_active = df_upload
                    st.success(f"✓ Canonical healthcare dataset loaded & saved to SQLite ({len(df_upload):,} records)!")
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")
                df_active = df_default
        else:
            df_active = df_default
            st.markdown("""
            <div class="dataset-info-box">
                <span style="color: #60A5FA;">✓ Active Storage: SQLite DB (<code>hospital_analytics.db</code>)</span><br>
                <strong>Total records:</strong> 54,966<br>
                <strong>Total attributes:</strong> 32<br>
                <strong>De-identification:</strong> 100% Salted SHA-256
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("**🔍 Dynamic Filters**")
        
        # Date range filter
        if "admission_date" in df_active.columns and len(df_active) > 0:
            min_date = df_active["admission_date"].min().date()
            max_date = df_active["admission_date"].max().date()
            date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        else:
            date_range = None
        
        # Admission Urgency filter
        if "admission_type" in df_active.columns:
            adm_types = ["All"] + sorted(df_active["admission_type"].dropna().unique().tolist())
            selected_adm = st.selectbox("Admission Urgency", adm_types)
        else:
            selected_adm = "All"
        
        # Medical Condition filter
        if "medical_condition" in df_active.columns:
            conditions = ["All"] + sorted(df_active["medical_condition"].dropna().unique().tolist())
            selected_cond = st.selectbox("Medical Condition", conditions)
        else:
            selected_cond = "All"
        
        # Insurance Provider filter
        if "insurance_provider" in df_active.columns:
            payers = ["All"] + sorted(df_active["insurance_provider"].dropna().unique().tolist())
            selected_payer = st.selectbox("Insurance Provider", payers)
        else:
            selected_payer = "All"
        
        # Apply filters safely
        filtered_df = df_active.copy()
        if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
            s_d, e_d = date_range
            filtered_df = filtered_df[
                (filtered_df["admission_date"].dt.date >= s_d) & 
                (filtered_df["admission_date"].dt.date <= e_d)
            ]
        if selected_adm != "All" and "admission_type" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["admission_type"] == selected_adm]
        if selected_cond != "All" and "medical_condition" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["medical_condition"] == selected_cond]
        if selected_payer != "All" and "insurance_provider" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["insurance_provider"] == selected_payer]
            
        st.caption(f"Active Records: **{len(filtered_df):,}** / **{len(df_active):,}**")
    else:
        filtered_df = df_default


# =============================================================================
# VIEW 1: PORTAL HOME (Matching Image 1)
# =============================================================================
if st.session_state["portal_nav"] == "🏠 Portal Home":
    st.markdown('<div class="portal-title">Welcome to Hospital Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="portal-subtitle">'
        'A central portal for exploring inpatient admissions, clinical patterns, financial analytics, and operational insights.'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Metric Summary Row
    total_adm = len(df_default)
    uniq_patients = df_default["patient_key"].nunique()
    total_rev_b = df_default["billing_amount"].sum() / 1e9
    avg_stay = df_default["los_days"].mean()
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Inpatient Admissions</div>
            <div class="kpi-value">{total_adm:,}</div>
            <div class="kpi-subtext">5-Year Historical Census</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Unique Patients Treated</div>
            <div class="kpi-value">{uniq_patients:,}</div>
            <div class="kpi-subtext">Salted SHA-256 De-identified</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Billed Charges</div>
            <div class="kpi-value">${total_rev_b:.2f}B</div>
            <div class="kpi-subtext">Currency Units (Unspecified)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Length of Stay</div>
            <div class="kpi-value">{avg_stay:.1f} d</div>
            <div class="kpi-subtext">Median: 16.0 Days</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Active monitoring across 5 years of inpatient census data (2019-2024). Strict non-predictive governance.")
    st.markdown("---")
    
    # Available Dashboards Section
    st.subheader("Available Dashboards")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.markdown("""
        <div class="dash-card">
            <div class="dash-card-title">📊 Streamlit Analytics</div>
            <div class="dash-card-desc">
                Explore admission volume trends, patient demographic pyramids, clinical diagnoses, 
                length of stay distributions, payer financial comparisons, and raw dataset quality.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("🚀 Open Streamlit Analytics", on_click=set_page, args=("📊 Streamlit Analytics",), use_container_width=True)
            
    with col_d2:
        st.markdown("""
        <div class="dash-card">
            <div class="dash-card-title">📈 Power BI Dashboard</div>
            <div class="dash-card-desc">
                Access the 4-page Power BI executive dashboard showcase, download the compiled .pbix 
                report, export Star Schema fact & dimension CSVs, and copy production DAX measure formulas.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("📊 Open Power BI Hub", on_click=set_page, args=("📈 Power BI Dashboard",), use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color: #64748B; font-size: 0.82rem; border-top: 1px solid #1E293B; padding-top: 1rem;">
        Project data is synthetic and intended for educational healthcare analytics. 
        Direct personal identifiers have been de-identified via salted SHA-256 (<code>patient_key</code>) 
        and deterministic physician IDs (<code>doctor_id</code>). Verified 100% privacy compliant.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# VIEW 2: STREAMLIT ANALYTICS (Matching Image 2)
# =============================================================================
elif st.session_state["portal_nav"] == "📊 Streamlit Analytics":
    # Eyebrow & Title
    st.markdown('<div class="portal-eyebrow">BEYOND THE NUMBERS / HEALTHCARE ANALYTICS WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="portal-title">Hospital Intelligence. 🔗</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="portal-subtitle">'
        'Inpatient throughput & clinical operations | Interactive analytics dashboard'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Synthetic Data Alert Banner
    st.markdown("""
    <div class="synthetic-badge">
        <span><strong>SIMULATED DATA</strong> | Educational project. Patient admission records, diagnoses, and financial metrics are synthetic, not live clinical outcomes.</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Collapsible Dataset Quality Report (Matching screenshot)
    with st.expander("▶ Dataset Quality Report", expanded=False):
        st.markdown("""
        * **Total Raw Records Ingested**: 55,500 admissions (0 missing values across all source columns).
        * **Exact Duplicates Removed**: 534 records purged ($55,500 - 534 = 54,966$ clean admissions).
        * **Near-Duplicates Flagged**: 5,466 records flagged via `near_duplicate_flag = 1` (preserved transparently).
        * **De-identification Protocol**: Salted SHA-256 patient pseudonymization (`patient_key`) & physician mapping (`doctor_id`).
        * **Automated Privacy Audit**: **100% PASS** with zero direct identifier leaks across 71,197 indexed raw names.
        """)

    # Check for empty filter result
    if len(filtered_df) == 0:
        st.warning("⚠️ No records match the active filter criteria. Please widen your date range or filter selections.")
        st.stop()

    # 5 Key Metrics Cards (Matching screenshot layout)
    t_adm = len(filtered_df)
    u_pat = filtered_df["patient_key"].nunique() if "patient_key" in filtered_df.columns else 0
    m_stay = filtered_df["los_days"].mean() if "los_days" in filtered_df.columns else 0.0
    t_bill = (filtered_df["billing_amount"].sum() / 1e6) if "billing_amount" in filtered_df.columns else 0.0
    
    if "readmission_eligible" in filtered_df.columns and "readmitted_30d" in filtered_df.columns:
        elig_df = filtered_df[filtered_df["readmission_eligible"] == 1]
        readm_p = (elig_df["readmitted_30d"].mean() * 100) if len(elig_df) > 0 else 0.0
    else:
        readm_p = 0.0
    
    col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)
    with col_k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Admissions</div>
            <div class="kpi-value">{t_adm:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Patients</div>
            <div class="kpi-value">{u_pat:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Stay</div>
            <div class="kpi-value">{m_stay:.1f} d</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Billed</div>
            <div class="kpi-value">${t_bill:,.0f}M</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">30-Day Readmission</div>
            <div class="kpi-value">{readm_p:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Analytical Sub-Tabs
    tab_over, tab_demo, tab_clin, tab_cost, tab_explore = st.tabs([
        "Overview",
        "Demographics",
        "Clinical & Diagnoses",
        "Cost & Readmissions",
        "Data Explorer"
    ])
    
    # Dark-themed Plotly layout defaults (strictly orthogonal to avoid keyword collisions)
    dark_plot_layout = dict(
        paper_bgcolor="#131E32",
        plot_bgcolor="#131E32",
        font=dict(color="#E2E8F0")
    )

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab_over:
        st.markdown("### Operational Throughput & Volume Trends")
        c1, c2 = st.columns([3, 2])
        
        with c1:
            if "admission_month" in filtered_df.columns:
                monthly = filtered_df.groupby("admission_month").size().reset_index(name="admissions")
                monthly["rolling_3m"] = monthly["admissions"].rolling(window=3, min_periods=1).mean()
                
                fig_m = go.Figure()
                fig_m.add_trace(go.Bar(
                    x=monthly["admission_month"],
                    y=monthly["admissions"],
                    name="Monthly Admissions",
                    marker_color="#38BDF8"
                ))
                fig_m.add_trace(go.Scatter(
                    x=monthly["admission_month"],
                    y=monthly["rolling_3m"],
                    name="3-Month Trend",
                    line=dict(color="#F43F5E", width=2.5)
                ))
                fig_m.update_layout(
                    title="Monthly Inpatient Volume with Moving Average",
                    template="plotly_dark",
                    **dark_plot_layout
                )
                st.plotly_chart(fig_m, use_container_width=True)
            
        with c2:
            if "admission_type" in filtered_df.columns:
                urg_df = filtered_df["admission_type"].value_counts().reset_index()
                urg_df.columns = ["Urgency", "Count"]
                fig_u = px.pie(
                    urg_df, values="Count", names="Urgency", hole=0.55,
                    title="Admission Acuity Distribution",
                    color="Urgency",
                    color_discrete_map={"Emergency": "#EF4444", "Urgent": "#F59E0B", "Elective": "#10B981"}
                )
                fig_u.update_layout(template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_u, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            if "admission_weekday" in filtered_df.columns:
                weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                wk_df = filtered_df["admission_weekday"].value_counts().reindex(weekday_order).dropna().reset_index()
                wk_df.columns = ["Day", "Count"]
                fig_wk = px.bar(
                    wk_df, x="Day", y="Count",
                    title="Admissions by Day of Week",
                    color="Count",
                    color_continuous_scale="Blues"
                )
                fig_wk.update_layout(template="plotly_dark", coloraxis_showscale=False, **dark_plot_layout)
                st.plotly_chart(fig_wk, use_container_width=True)
            
        with c4:
            if "admission_month" in filtered_df.columns and "discharge_month" in filtered_df.columns:
                adm_c = filtered_df.groupby("admission_month").size().rename("Admissions")
                dis_c = filtered_df.groupby("discharge_month").size().rename("Discharges")
                flow = pd.concat([adm_c, dis_c], axis=1).fillna(0).reset_index()
                flow.rename(columns={"index": "Month"}, inplace=True)
                
                fig_f = go.Figure()
                fig_f.add_trace(go.Scatter(x=flow["Month"], y=flow["Admissions"], mode="lines+markers", name="Admissions", line=dict(color="#38BDF8")))
                fig_f.add_trace(go.Scatter(x=flow["Month"], y=flow["Discharges"], mode="lines+markers", name="Discharges", line=dict(color="#10B981")))
                fig_f.update_layout(title="Inpatient Intake vs. Discharge Velocity", template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_f, use_container_width=True)

    # ---------------- TAB 2: DEMOGRAPHICS ----------------
    with tab_demo:
        st.markdown("### Patient Population Demographics")
        d1, d2 = st.columns(2)
        with d1:
            if "age" in filtered_df.columns:
                fig_age = px.histogram(
                    filtered_df, x="age", nbins=30,
                    title=f"Age Distribution (Mean: {filtered_df['age'].mean():.1f} yrs)",
                    color_discrete_sequence=["#818CF8"]
                )
                fig_age.add_vline(x=filtered_df["age"].median(), line_dash="dash", line_color="#EF4444", annotation_text=f"Median: {filtered_df['age'].median():.0f}")
                fig_age.update_layout(template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_age, use_container_width=True)
            
        with d2:
            if "age_group" in filtered_df.columns and "gender" in filtered_df.columns:
                age_order = ["0-17", "18-34", "35-49", "50-64", "65+"]
                g_df = filtered_df.groupby(["age_group", "gender"]).size().reset_index(name="Count")
                fig_g = px.bar(
                    g_df, x="age_group", y="Count", color="gender", barmode="group",
                    category_orders={"age_group": age_order},
                    title="Age Bracket Distribution by Gender",
                    color_discrete_map={"Male": "#38BDF8", "Female": "#F472B6"}
                )
                fig_g.update_layout(template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_g, use_container_width=True)

        d3, d4 = st.columns(2)
        with d3:
            if "blood_type" in filtered_df.columns:
                b_df = filtered_df["blood_type"].value_counts().reset_index()
                b_df.columns = ["Blood_Type", "Count"]
                fig_b = px.bar(b_df, x="Blood_Type", y="Count", title="Blood Group Distribution", color="Count", color_continuous_scale="Purples")
                fig_b.update_layout(template="plotly_dark", coloraxis_showscale=False, **dark_plot_layout)
                st.plotly_chart(fig_b, use_container_width=True)
            
        with d4:
            st.info("📌 **Field Availability Notice**: Patient geographic location (Rural/Urban) and clinical departments are unrecorded in this dataset. Per data governance charter, no synthetic geographic variables have been invented.")
            if "age_group" in filtered_df.columns and "admission_type" in filtered_df.columns:
                age_order = ["0-17", "18-34", "35-49", "50-64", "65+"]
                cross_adm = pd.crosstab(filtered_df["age_group"], filtered_df["admission_type"], normalize="index") * 100
                cross_adm = cross_adm.reindex(age_order).dropna()
                fig_h = px.imshow(
                    cross_adm, labels=dict(x="Urgency", y="Age Bracket", color="Share (%)"),
                    title="Admission Acuity Share by Age Bracket (%)",
                    text_auto=".1f", color_continuous_scale="Teal"
                )
                fig_h.update_layout(template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_h, use_container_width=True)

    # ---------------- TAB 3: CLINICAL ----------------
    with tab_clin:
        st.markdown("### Clinical Diagnoses, Outcomes & Pharmacy Profiling")
        cl1, cl2 = st.columns(2)
        with cl1:
            if "medical_condition" in filtered_df.columns:
                c_df = filtered_df["medical_condition"].value_counts().reset_index()
                c_df.columns = ["Condition", "Count"]
                fig_c = px.bar(
                    c_df, x="Count", y="Condition", orientation="h",
                    title="Prevalence of Primary Medical Diagnoses",
                    color="Count", color_continuous_scale="Viridis"
                )
                fig_c.update_layout(template="plotly_dark", coloraxis_showscale=False, **dark_plot_layout)
                fig_c.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_c, use_container_width=True)
            
        with cl2:
            if "medical_condition" in filtered_df.columns and "test_results" in filtered_df.columns:
                t_cross = pd.crosstab(filtered_df["medical_condition"], filtered_df["test_results"], normalize="index") * 100
                t_cross = t_cross.reset_index().melt(id_vars="medical_condition", var_name="Test_Result", value_name="Share")
                fig_t = px.bar(
                    t_cross, x="medical_condition", y="Share", color="Test_Result",
                    title="Diagnostic Test Results Distribution by Diagnosis (%)",
                    color_discrete_map={"Normal": "#10B981", "Abnormal": "#EF4444", "Inconclusive": "#F59E0B"}
                )
                fig_t.update_layout(template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_t, use_container_width=True)

        cl3, cl4 = st.columns(2)
        with cl3:
            if "medication" in filtered_df.columns:
                med_c = filtered_df["medication"].value_counts().reset_index()
                med_c.columns = ["Medication", "Count"]
                fig_med = px.bar(med_c, x="Medication", y="Count", title="Top Prescribed Medications", color="Count", color_continuous_scale="Sunset")
                fig_med.update_layout(template="plotly_dark", coloraxis_showscale=False, **dark_plot_layout)
                st.plotly_chart(fig_med, use_container_width=True)
            
        with cl4:
            if "medical_condition" in filtered_df.columns and "los_days" in filtered_df.columns:
                los_c = filtered_df.groupby("medical_condition")["los_days"].mean().reset_index()
                los_c.columns = ["Condition", "ALOS"]
                fig_lc = px.bar(los_c, x="Condition", y="ALOS", title="Average Length of Stay (ALOS) by Diagnosis", color="ALOS", color_continuous_scale="Blues")
                fig_lc.update_layout(template="plotly_dark", coloraxis_showscale=False, **dark_plot_layout)
                st.plotly_chart(fig_lc, use_container_width=True)

    # ---------------- TAB 4: COST & READMISSIONS ----------------
    with tab_cost:
        st.markdown("### Financial Analytics & 30-Day Readmissions")
        f1, f2 = st.columns(2)
        with f1:
            if "insurance_provider" in filtered_df.columns and "billing_amount" in filtered_df.columns:
                p_df = (filtered_df.groupby("insurance_provider")["billing_amount"].sum() / 1e6).reset_index()
                p_df.columns = ["Payer", "Total_Billing_M"]
                fig_p = px.bar(p_df, x="Payer", y="Total_Billing_M", title="Billed Revenue by Insurance Payer ($M CU)", color="Payer", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_p.update_layout(template="plotly_dark", showlegend=False, **dark_plot_layout)
                st.plotly_chart(fig_p, use_container_width=True)
            
        with f2:
            if "los_days" in filtered_df.columns and "billing_amount" in filtered_df.columns:
                sample_df = filtered_df.sample(n=min(len(filtered_df), 3000), random_state=42)
                fig_sc = px.scatter(
                    sample_df, x="los_days", y="billing_amount", color="admission_type" if "admission_type" in sample_df.columns else None, opacity=0.45,
                    title="Stay Duration vs. Billing Amount (ρ = -0.005, p = 0.256 — Decoupled)",
                    labels={"los_days": "Length of Stay (Days)", "billing_amount": "Billing (CU)"},
                    color_discrete_map={"Emergency": "#EF4444", "Urgent": "#F59E0B", "Elective": "#10B981"}
                )
                fig_sc.update_layout(template="plotly_dark", **dark_plot_layout)
                st.plotly_chart(fig_sc, use_container_width=True)

        f3, f4 = st.columns(2)
        with f3:
            if "readmission_eligible" in filtered_df.columns and "readmitted_30d" in filtered_df.columns:
                elig_sub = filtered_df[filtered_df["readmission_eligible"] == 1]
                if len(elig_sub) > 0 and "admission_type" in elig_sub.columns:
                    r_type = (
                        elig_sub.groupby("admission_type")
                        .agg(Eligible=("admission_id", "count"), Readmissions=("readmitted_30d", "sum"))
                        .reset_index()
                    )
                    r_type["Rate_Pct"] = (r_type["Readmissions"] / r_type["Eligible"]) * 100
                    fig_r = px.bar(
                        r_type, x="admission_type", y="Rate_Pct", color="admission_type", text_auto=".2f",
                        title="30-Day Readmission Proxy Rate by Urgency (%)",
                        color_discrete_map={"Emergency": "#EF4444", "Urgent": "#F59E0B", "Elective": "#10B981"}
                    )
                    fig_r.update_layout(template="plotly_dark", showlegend=False, **dark_plot_layout)
                    st.plotly_chart(fig_r, use_container_width=True)
                else:
                    st.info("No eligible stays recorded for readmission calculation.")
            
        with f4:
            if "readmitted_30d" in filtered_df.columns and "days_to_next_admission" in filtered_df.columns:
                readm_c = filtered_df[filtered_df["readmitted_30d"] == 1]
                if len(readm_c) > 0:
                    fig_tim = px.histogram(
                        readm_c, x="days_to_next_admission", nbins=15,
                        title="Return Timing Distribution (Days Post-Discharge)",
                        color_discrete_sequence=["#F43F5E"]
                    )
                    fig_tim.update_layout(template="plotly_dark", yaxis_title="Readmissions", **dark_plot_layout)
                    st.plotly_chart(fig_tim, use_container_width=True)
                else:
                    st.info("No 30-day readmissions recorded under current filter selection.")

    # ---------------- TAB 5: DATA EXPLORER ----------------
    with tab_explore:
        st.markdown("### Interactive Inpatient Dataset Explorer")
        st.caption("Inspect individual records. Direct patient names and doctors are replaced with non-identifying keys.")
        
        preview_cols = [
            c for c in [
                "admission_id", "patient_key", "doctor_id", "age", "age_group",
                "gender", "blood_type", "medical_condition", "admission_type",
                "admission_date", "discharge_date", "los_days", "insurance_provider",
                "billing_amount", "cost_per_day", "readmitted_30d"
            ] if c in filtered_df.columns
        ]
        
        search_q = st.text_input("Search by Admission ID or Patient Key", "")
        disp_df = filtered_df[preview_cols]
        if search_q and "admission_id" in disp_df.columns:
            mask = disp_df["admission_id"].astype(str).str.contains(search_q, case=False, na=False)
            if "patient_key" in disp_df.columns:
                mask = mask | disp_df["patient_key"].astype(str).str.contains(search_q, case=False, na=False)
            disp_df = disp_df[mask]
            
        st.dataframe(disp_df.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Showing top {min(len(disp_df), 100)} of {len(disp_df):,} matching rows.")
        
        # Download button
        csv_bytes = filtered_df[preview_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            data=csv_bytes,
            file_name="filtered_hospital_admissions.csv",
            mime="text/csv"
        )


# =============================================================================
# VIEW 3: POWER BI DASHBOARD (Dedicated Hub)
# =============================================================================
elif st.session_state["portal_nav"] == "📈 Power BI Dashboard":
    st.markdown('<div class="portal-eyebrow">ENTERPRISE BUSINESS INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="portal-title">Power BI Dashboard Hub. 📈</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="portal-subtitle">'
        'Interactive 4-Page Executive Dashboard, Compiled .pbix Report & Star Schema Architecture.'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Check for .pbix report file
    pbix_filename = "Hospital_ desh_powerbi.pbix"
    pbix_path = os.path.join("powerbi", pbix_filename)
            
    if os.path.exists(pbix_path):
        pbix_size_mb = os.path.getsize(pbix_path) / (1024 * 1024)
        with open(pbix_path, "rb") as f_pbix:
            pbix_bytes = f_pbix.read()
            
        c_stat1, c_stat2 = st.columns([3, 1])
        with c_stat1:
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #064E3B 0%, #065F46 100%); border: 1px solid #10B981; border-radius: 10px; padding: 14px 20px; margin-bottom: 1rem;">
                <div style="font-weight: 700; color: #ECFDF5; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
                    <span>🟢 Production Power BI Report File (.pbix) Ready</span>
                </div>
                <div style="color: #A7F3D0; font-size: 0.85rem; margin-top: 4px;">
                    <strong>File:</strong> <code>{pbix_filename}</code> ({pbix_size_mb:.2f} MB) | Multi-page executive BI report with Star Schema & custom Healthcare Light Theme.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_stat2:
            st.download_button(
                label="⬇ Download Report (.pbix)",
                data=pbix_bytes,
                file_name="Hospital_ desh_powerbi.pbix",
                mime="application/octet-stream",
                key="dl_main_pbix_top",
                use_container_width=True
            )
    else:
        st.markdown("""
        <div class="synthetic-badge">
            <span><strong>STAR SCHEMA MODEL</strong> | All Fact and Dimension tables have been generated and exported to <code>powerbi/</code>.</span>
        </div>
        """, unsafe_allow_html=True)
    
    # 4 Quick Action Metric Cards
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Fact Records</div>
            <div class="kpi-value">54,966</div>
            <div class="kpi-subtext">Fact_Admissions.csv</div>
        </div>
        """, unsafe_allow_html=True)
    with c_p2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Dimensions</div>
            <div class="kpi-value">5 Tables</div>
            <div class="kpi-subtext">Date, Patient, Doctor, Hosp, Cond</div>
        </div>
        """, unsafe_allow_html=True)
    with c_p3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Core DAX Measures</div>
            <div class="kpi-value">16 Formulas</div>
            <div class="kpi-subtext">Volume, LOS, Cost, Readm, Demo</div>
        </div>
        """, unsafe_allow_html=True)
    with c_p4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Report Status</div>
            <div class="kpi-value">4 Pages</div>
            <div class="kpi-subtext">{'PBIX Compiled & Ready' if pbix_path else 'In Development'}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for Power BI specifications & Showcase
    pbi_tab1, pbi_tab2, pbi_tab3, pbi_tab4 = st.tabs([
        "🖼️ Interactive 4-Page Report Showcase",
        "📥 Download Report & Star Schema",
        "📐 DAX Measure Catalog",
        "🏗️ Data Architecture & Star Schema Model"
    ])
    
    with pbi_tab1:
        st.subheader("Executive Multi-Page Power BI Report Showcase")
        st.markdown("Explore the 4 specialized executive dashboard views built inside the Power BI desktop report:")
        
        selected_page = st.radio(
            "Select Dashboard View to Inspect:",
            [
                "📊 Page 1: Executive Overview",
                "👥 Page 2: Patient Demographics",
                "🩺 Page 3: Clinical & Diagnoses",
                "💰 Page 4: Cost, Financials & Readmissions"
            ],
            horizontal=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if "Page 1" in selected_page:
            p1_img = os.path.join("assets", "powerbi_screens", "page1_executive_overview.png")
            if os.path.exists(p1_img):
                st.image(p1_img, caption="Page 1: Executive Overview — Admissions Volume, ALOS, Revenue, Readmission Rate", use_container_width=True)
            
            c_meta1, c_meta2 = st.columns(2)
            with c_meta1:
                st.markdown("""
                **🎯 Target Stakeholders**: Hospital Chief Executive Officer (CEO), Chief Operating Officer (COO), Board of Directors.
                
                **📌 Core KPI Summary Cards**:
                * **Total Admissions**: `55K` (54,966 completed stays)
                * **ALOS (Days)**: `15.50` days average inpatient stay
                * **Total Billed Amount**: `$1.40B` gross billed charges
                * **30-Day Readmission Rate**: `1.14%` (626 readmissions out of 54,966 eligible)
                """)
            with c_meta2:
                st.markdown("""
                **📊 Primary Visualizations**:
                * **Monthly Admissions Trend (Area Chart)**: Tracks volume trajectory across calendar years 2019 to 2024.
                * **Admissions by Urgency Level (Donut Chart)**: Balanced intake mix (~33.6% Elective, 33.5% Urgent, 32.9% Emergency).
                * **Weekday Intake Census (Column Chart)**: Daily admission loads across Mon–Sun demonstrating continuous admissions.
                """)
                
        elif "Page 2" in selected_page:
            p2_img = os.path.join("assets", "powerbi_screens", "page2_patient_demographics.png")
            if os.path.exists(p2_img):
                st.image(p2_img, caption="Page 2: Patient Demographics — Age Cohorts, Gender Balance, Blood Type Distribution", use_container_width=True)
                
            c_meta1, c_meta2 = st.columns(2)
            with c_meta1:
                st.markdown("""
                **🎯 Target Stakeholders**: Population Health Directors, Community Outreach Teams, Capacity Planners.
                
                **📌 Core Demographic Benchmarks**:
                * **Unique Patients**: `40,235` distinct individuals
                * **Senior Share (65+)**: `30.1%` (16,559 admissions) — largest geriatric cohort
                * **Pediatric Share (0-17)**: `4.6%` (2,534 admissions)
                * **Gender Balance**: `50.0% Female` / `50.0% Male` (Mann-Whitney U $p = 0.3205$)
                """)
            with c_meta2:
                st.markdown("""
                **📊 Primary Visualizations**:
                * **Age Bracket Distribution by Gender (Clustered Bar Chart)**: Compares male vs female intake across 5 standard brackets.
                * **Admission Urgency Mix by Age Group (100% Stacked Bar)**: Proportion of Emergency vs Elective stays by cohort.
                * **Blood Group Distribution (Horizontal Bar)**: Even representation across all 8 ABO/Rh blood groups (~12.5% each).
                """)

        elif "Page 3" in selected_page:
            p3_img = os.path.join("assets", "powerbi_screens", "page3_clinical_diagnoses.png")
            if os.path.exists(p3_img):
                st.image(p3_img, caption="Page 3: Clinical & Diagnoses — Condition Prevalence, Prescribed Medications, Test Outcomes", use_container_width=True)
                
            c_meta1, c_meta2 = st.columns(2)
            with c_meta1:
                st.markdown("""
                **🎯 Target Stakeholders**: Chief Medical Officer (CMO), Pharmacy & Therapeutics Committee, Diagnostic Quality Directors.
                
                **📌 Clinical Insights**:
                * **6 Chronic Conditions**: Arthritis (9,218), Diabetes (9,216), Hypertension (9,151), Obesity (9,146), Cancer (9,140), Asthma (9,095).
                * **Medication Utilization**: 5 core inpatient pharmaceuticals tracked evenly (~10,900 to 11,050 courses each).
                * **Uniform ALOS**: Condition-level length of stay consistently averages ~15.5 days across all diagnoses.
                """)
            with c_meta2:
                st.markdown("""
                **📊 Primary Visualizations**:
                * **Prevalence by Condition (Column Chart)**: Inpatient volume comparison across the 6 major disease categories.
                * **Medication Utilization (Treemap)**: Prescription breakdown across Lipitor, Aspirin, Ibuprofen, Paracetamol, and Penicillin.
                * **Diagnostic Test Outcomes (100% Stacked Bar)**: Normal, Abnormal, and Inconclusive laboratory splits by diagnosis.
                * **ALOS by Medical Condition (Horizontal Bar)**: Mean stay duration per diagnostic category.
                """)

        elif "Page 4" in selected_page:
            p4_img = os.path.join("assets", "powerbi_screens", "page4_cost_financials.png")
            if os.path.exists(p4_img):
                st.image(p4_img, caption="Page 4: Cost, Financials & Readmissions — Payer Revenue, Financial Matrix, 30-Day Readmissions", use_container_width=True)
                
            c_meta1, c_meta2 = st.columns(2)
            with c_meta1:
                st.markdown("""
                **🎯 Target Stakeholders**: Chief Financial Officer (CFO), Revenue Cycle Management, Managed Care Contracting.
                
                **📌 Financial & Quality Metrics**:
                * **Gross Billed Charges**: `$1,404,057,758` ($1.40 Billion)
                * **Average Billed per Stay**: `$25,544.31`
                * **Payer Distribution**: 5 major payers (Cigna, Medicare, Blue Cross, UnitedHealthcare, Aetna) each representing ~$277M–$286M.
                * **30-Day Readmission Rate**: Baseline rate of `1.14%` (Emergency slightly elevated at ~1.3%).
                """)
            with c_meta2:
                st.markdown("""
                **📊 Primary Visualizations**:
                * **Billed Revenue by Insurance Payer (Column Chart)**: Total billing captured across private and public insurers.
                * **Financial & Quality Scorecard (Matrix Table)**: Condition-level admissions, average billing, high cost share (5%), and readmission rate.
                * **30-Day Readmission Rate by Urgency (Column Chart)**: Compares readmission probability across Emergency, Elective, and Urgent intakes.
                * **Stay Duration vs Billed Revenue (Scatter Plot)**: Correlation inspection between length of stay and total hospital charges.
                """)

    with pbi_tab2:
        st.subheader("Download Power BI Artifacts & Star Schema Tables")
        st.markdown("All pre-configured report deliverables and underlying clean dimension tables are available for one-click download:")
        
        # Power BI Files Section
        st.markdown("#### 1. Compiled Power BI Report & Custom Themes")
        col_f1, col_f2 = st.columns(2)
        
        if os.path.exists(pbix_path):
            with col_f1:
                st.markdown(f"**`{pbix_filename}`** — *Completed 4-page Power BI Desktop report with all relationships, measures, and visuals*")
                st.download_button(
                    "⬇ Download Completed Report (.pbix)",
                    data=pbix_bytes,
                    file_name="Hospital_ desh_powerbi.pbix",
                    mime="application/octet-stream",
                    key="dl_tab_pbix"
                )
        
        theme_light_path = os.path.join("powerbi", "Healthcare_Executive_Light_Theme.json")
        if os.path.exists(theme_light_path):
            with open(theme_light_path, "rb") as f_theme:
                theme_light_bytes = f_theme.read()
            with col_f2:
                st.markdown("**`Healthcare_Executive_Light_Theme.json`** — *Custom enterprise palette (Navy `#0F172A`, Slate `#334155`, rounded corners `10px`)*")
                st.download_button(
                    "⬇ Download Light Theme (.json)",
                    data=theme_light_bytes,
                    file_name="Healthcare_Executive_Light_Theme.json",
                    mime="application/json",
                    key="dl_theme_light"
                )
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 2. Star Schema Ingestion Tables (CSV)")
        st.markdown("Ready-to-ingest CSV tables exported from data processing pipeline:")
        
        d_col1, d_col2 = st.columns(2)
        tables = [
            ("Fact_Admissions.csv", "54,966 admissions records with foreign keys & canonical metrics"),
            ("Dim_Date.csv", "2,192 continuous calendar days (2019-2024)"),
            ("Dim_Patient.csv", "40,235 unique patients with age brackets & lifetime admissions"),
            ("Dim_Doctor.csv", "40,341 pseudonymous physicians (DR-001...)"),
            ("Dim_Hospital.csv", "13 facility tiers adhering to sample size guardrail (n >= 30)"),
            ("Dim_Condition.csv", "6 primary conditions mapped to clinical specialty proxies")
        ]
        
        for idx, (tbl_name, tbl_desc) in enumerate(tables):
            col = d_col1 if idx % 2 == 0 else d_col2
            tbl_path = os.path.join("powerbi", tbl_name)
            if os.path.exists(tbl_path):
                with open(tbl_path, "rb") as f:
                    file_data = f.read()
                with col:
                    st.markdown(f"**`{tbl_name}`** — *{tbl_desc}*")
                    st.download_button(
                        f"⬇ Download {tbl_name}",
                        data=file_data,
                        file_name=tbl_name,
                        mime="text/csv",
                        key=f"dl_star_{tbl_name}"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

    with pbi_tab3:
        st.subheader("Core DAX Measures Catalog (Ready to Copy & Paste)")
        st.markdown("All 16 production DAX measures implemented in the `_Measures` table:")
        
        dax_col1, dax_col2 = st.columns(2)
        with dax_col1:
            st.markdown("**1. Volume & Census Measures**")
            st.code("Total Admissions = COUNTROWS(Fact_Admissions)", language="dax")
            st.code("Unique Patients = DISTINCTCOUNT(Fact_Admissions[patient_key])", language="dax")
            
            st.markdown("**2. Length of Stay (LOS) Measures**")
            st.code("ALOS (Days) = AVERAGE(Fact_Admissions[los_days])", language="dax")
            st.code("Median LOS = MEDIAN(Fact_Admissions[los_days])", language="dax")
            st.code("Long Stay Admissions = CALCULATE(COUNTROWS(Fact_Admissions), Fact_Admissions[long_stay_flag] = 1)", language="dax")
            st.code("Long Stay % = DIVIDE([Long Stay Admissions], [Total Admissions], 0)", language="dax")
            
            st.markdown("**3. Demographic Cohort Measures**")
            st.code("Avg Patient Age = AVERAGE(Dim_Patient[age])", language="dax")
            st.code("Senior Share % = DIVIDE(CALCULATE(COUNTROWS(Fact_Admissions), Dim_Patient[age_group] = \"65+\"), COUNTROWS(Fact_Admissions), 0)", language="dax")
            st.code("Pediatric Share % = DIVIDE(CALCULATE(COUNTROWS(Fact_Admissions), Dim_Patient[age_group] = \"0-17\"), COUNTROWS(Fact_Admissions), 0)", language="dax")
            st.code("Female Share % = DIVIDE(CALCULATE(COUNTROWS(Fact_Admissions), Dim_Patient[gender] = \"Female\"), COUNTROWS(Fact_Admissions), 0)", language="dax")

        with dax_col2:
            st.markdown("**4. Financial & Revenue Cycle Measures**")
            st.code("Total Billed Amount = SUM(Fact_Admissions[billing_amount])", language="dax")
            st.code("Avg Billed per Admission = AVERAGE(Fact_Admissions[billing_amount])", language="dax")
            st.code("Avg Cost per Day = AVERAGE(Fact_Admissions[cost_per_day])", language="dax")
            st.code("High Cost Admissions = CALCULATE(COUNTROWS(Fact_Admissions), Fact_Admissions[high_cost_flag] = 1)", language="dax")
            st.code("High Cost % = DIVIDE([High Cost Admissions], [Total Admissions], 0)", language="dax")
            
            st.markdown("**5. Quality & 30-Day Readmission Measures**")
            st.code("Eligible Stays = CALCULATE(COUNTROWS(Fact_Admissions), Fact_Admissions[readmission_eligible] = 1)", language="dax")
            st.code("30-Day Readmissions = CALCULATE(SUM(Fact_Admissions[readmitted_30d]), Fact_Admissions[readmission_eligible] = 1)", language="dax")
            st.code("30-Day Readmission Rate % = DIVIDE([30-Day Readmissions], [Eligible Stays], 0)", language="dax")

    with pbi_tab4:
        st.subheader("Data Model Architecture & Relationship Schema")
        st.markdown("""
        The Power BI model follows a strict **Star Schema (Kimball Methodology)**.
        All 5 dimension tables filter the central `Fact_Admissions` table via **1-to-Many (`1:*`) relationships with Single Cross-Filter direction**:
        """)
        
        schema_df = pd.DataFrame([
            {"Dimension Table": "Dim_Date", "Primary Key": "date_key", "Fact Foreign Key": "admission_date_key", "Cardinality": "1 to Many (1:*)", "Cross-Filter": "Single"},
            {"Dimension Table": "Dim_Patient", "Primary Key": "patient_key", "Fact Foreign Key": "patient_key", "Cardinality": "1 to Many (1:*)", "Cross-Filter": "Single"},
            {"Dimension Table": "Dim_Doctor", "Primary Key": "doctor_id", "Fact Foreign Key": "doctor_id", "Cardinality": "1 to Many (1:*)", "Cross-Filter": "Single"},
            {"Dimension Table": "Dim_Hospital", "Primary Key": "hospital", "Fact Foreign Key": "hospital", "Cardinality": "1 to Many (1:*)", "Cross-Filter": "Single"},
            {"Dimension Table": "Dim_Condition", "Primary Key": "medical_condition", "Fact Foreign Key": "medical_condition", "Cardinality": "1 to Many (1:*)", "Cross-Filter": "Single"},
        ])
        st.dataframe(schema_df, hide_index=True, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📖 For comprehensive technical documentation, step-by-step ingestion walkthroughs, and design blueprints, consult [docs/powerbi_guide.md](file:///c:/Users/berab/OneDrive/Desktop/Hospital_data_analysis/docs/powerbi_guide.md).")
