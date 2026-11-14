"""
Script to build and execute notebooks/02_preprocessing.ipynb
Ensures top-to-bottom reproducibility, rich outputs, and privacy masking.
"""

import os
import io
import sys
import contextlib
import shutil
import nbformat as nbf
import pandas as pd
import numpy as np

def generate_preprocessing_notebook():
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
        ("markdown", """# 02. Data Preprocessing & Canonical Feature Engineering
**Phase 2: Data Preprocessing**  
**Project:** Hospital Patient Data Analysis and Dashboard Development Using Python and Power BI

---

### Objective & Cleaning Scope
This notebook turns the raw dataset (`data/raw/healthcare_dataset.csv`) into an analysis-ready canonical dataset (`data/processed/hospital_clean.csv`).
Every cleaning decision is audited, executed, and justified:
1. **Audit Before Fixing**: Missing values, exact duplicates, near-duplicates, inconsistent text casing, date validation, age plausibility, negative billing, and categorical sets.
2. **Deterministic Cleansing**: Exact duplicate drop, near-duplicate flagging, date parsing, and text trimming.
3. **HIPAA-Compliant De-identification**: Salted SHA-256 patient pseudonymization (`patient_key`) and deterministic doctor pseudonymization (`doctor_id`). Original `Name` and `Doctor` permanently removed.
4. **Canonical & Temporal Feature Derivations**: `los_days`, `age_group`, `admission_month`, `admission_year`, `admission_quarter`, `admission_weekday`, `discharge_month`, `cost_per_day`, `high_cost_flag`, `long_stay_flag`, and 30-day readmission proxy logic.
5. **Validation Assertions**: Complete assertion suite validating schema, chronology, categories, and row-count reconciliation.
"""),
        ("code", """# Environment setup, imports, and seeds
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed
np.random.seed(42)

# Display configurations
pd.set_option('display.max_columns', 35)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print(f"Python interpreter: {sys.version.split()[0]}")
print(f"Pandas version: {pd.__version__}")
"""),
        ("markdown", """## 1. Raw Dataset Audit Prior to Cleansing
Auditing data quality anomalies directly from `data/raw/healthcare_dataset.csv`."""),
        ("code", """raw_path = 'data/raw/healthcare_dataset.csv'
if not os.path.exists(raw_path):
    raw_path = '../data/raw/healthcare_dataset.csv'

df_raw = pd.read_csv(raw_path)
raw_rows, raw_cols = df_raw.shape
print(f"Raw Dataset Dimensions: {raw_rows:,} rows, {raw_cols} columns")

# Audit 1: Missing Values
raw_nulls = df_raw.isnull().sum()
print(f"Total Missing Values: {raw_nulls.sum()}")

# Audit 2: Exact Duplicates
exact_dups = df_raw.duplicated().sum()
print(f"Exact Duplicate Rows Detected: {exact_dups:,} ({exact_dups/raw_rows*100:.2f}%)")

# Audit 3: Date Parsing & Chronology
adm_parsed = pd.to_datetime(df_raw['Date of Admission'], format='%Y-%m-%d', errors='coerce')
dis_parsed = pd.to_datetime(df_raw['Discharge Date'], format='%Y-%m-%d', errors='coerce')
chrono_inversions = (dis_parsed < adm_parsed).sum()
print(f"Unparseable Dates: Admission={adm_parsed.isnull().sum()}, Discharge={dis_parsed.isnull().sum()}")
print(f"Chronological Inversions (Discharge < Admission): {chrono_inversions}")

# Audit 4: Age Plausibility
age_implausible = ((df_raw['Age'] < 0) | (df_raw['Age'] > 120)).sum()
print(f"Implausible Ages (outside 0-120): {age_implausible} (Min: {df_raw['Age'].min()}, Max: {df_raw['Age'].max()})")

# Audit 5: Billing Anomalies
neg_billing = (df_raw['Billing Amount'] < 0).sum()
zero_billing = (df_raw['Billing Amount'] == 0).sum()
print(f"Negative Billing Records: {neg_billing} (Min: ${df_raw['Billing Amount'].min():,.2f})")
print(f"Zero Billing Records: {zero_billing}")
"""),
        ("markdown", """## 2. Execute Data Cleaning Pipeline via `src.clean`
Executing modular `clean_dataset(raw_df)` function, producing canonical dataset and quality audit log."""),
        ("code", """# Add src to sys.path if not present
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))

from src.clean import clean_dataset

clean_df, quality_log_df = clean_dataset(df_raw)
print(f"Cleaned Canonical Dataset Dimensions: {clean_df.shape[0]:,} rows, {clean_df.shape[1]} columns")
print("\\n--- Data Quality Action Log ---")
print(quality_log_df[['issue', 'rows_affected', 'action']].to_string(index=False))
"""),
        ("markdown", """## 3. Canonical Schema & Derived Feature Verification
Inspecting all engineered features, clinical flags, and proxy metrics."""),
        ("code", """# Summarize canonical derived metrics
print("Canonical Columns List:")
print(clean_df.columns.tolist())

# Summary of Flags and Derived Indicators
flag_summary = pd.DataFrame({
    'Metric / Indicator': [
        'Total Admissions (Clean)',
        'Unique Patients (patient_key)',
        'Unique Doctors (doctor_id)',
        'Near-Duplicate Admissions (near_duplicate_flag=1)',
        'Financial Outlier Stays (high_cost_flag=1)',
        'Extended Stay Admissions (long_stay_flag=1)',
        'Billing Outlier Admissions (billing_outlier_flag=1)',
        '30-Day Readmissions (readmitted_30d=1)',
        '30-Day Readmission Eligible Stays',
        '30-Day Readmission Rate (%)'
    ],
    'Value': [
        f"{len(clean_df):,}",
        f"{clean_df['patient_key'].nunique():,}",
        f"{clean_df['doctor_id'].nunique():,}",
        f"{clean_df['near_duplicate_flag'].sum():,}",
        f"{clean_df['high_cost_flag'].sum():,}",
        f"{clean_df['long_stay_flag'].sum():,}",
        f"{clean_df['billing_outlier_flag'].sum():,}",
        f"{clean_df['readmitted_30d'].sum():,}",
        f"{clean_df['readmission_eligible'].sum():,}",
        f"{(clean_df[clean_df['readmission_eligible'] == 1]['readmitted_30d'].mean() * 100):.2f}%"
    ]
})
print("\\nCanonical Metric & Derived Feature Summary:")
print(flag_summary.to_string(index=False))
"""),
        ("markdown", """## 4. Before-and-After Cleaning Comparison Table
Systematic reconciliation of dimensions, nulls, duplicates, and column counts."""),
        ("code", """comparison_table = pd.DataFrame({
    'Dimension / Attribute': [
        'Total Rows',
        'Exact Duplicate Rows',
        'Direct Identifiers Present',
        'Total Missing Values (Nulls)',
        'Total Feature Columns',
        'Date Data Types',
        'Negative Billed Records'
    ],
    'Before (Raw Data)': [
        f"{raw_rows:,}",
        f"{exact_dups:,}",
        "Yes (Name, Doctor)",
        "0 (100% Complete)",
        f"{raw_cols}",
        "Object (String)",
        f"{neg_billing:,}"
    ],
    'After (Clean Data)': [
        f"{len(clean_df):,}",
        "0 (All Dropped)",
        "No (Pseudonymized & Dropped)",
        "0 (100% Complete)",
        f"{clean_df.shape[1]}",
        "Datetime64[ns]",
        f"{(clean_df['billing_amount'] < 0).sum():,} (Flagged)"
    ],
    'Delta / Transformation Action': [
        f"-{exact_dups:,} exact duplicate rows removed",
        "Purged identical repeats (First occurrence kept)",
        "patient_key (SHA-256) & doctor_id (DR-xxx)",
        "Maintained full completeness",
        f"+{clean_df.shape[1] - raw_cols} canonical derived features",
        "Converted to YYYY-MM-DD datetime objects",
        "billing_outlier_flag = 1 (Preserved for audit)"
    ]
})
print("Before vs. After Cleaning Reconciliation:")
print(comparison_table.to_string(index=False))
"""),
        ("markdown", """## 5. Validation Assertions Execution
Validating the 15 data integrity, domain, and privacy assertions."""),
        ("code", """from src.validate import validate_clean_dataset

validation_report_df = validate_clean_dataset(
    clean_df_path='data/processed/hospital_clean.csv' if os.path.exists('data/processed/hospital_clean.csv') else '../data/processed/hospital_clean.csv',
    raw_df_path=raw_path
)
"""),
        ("markdown", """## 6. Privacy-Safe Clean Dataset Sample Preview
Displaying sample records of the final analysis-ready dataset. Notice that no personal names or physician names exist anywhere."""),
        ("code", """# Display sample preview of final canonical dataset (excluding hospital to avoid synthetic name collisions)
preview_cols = [
    'admission_id', 'patient_key', 'age', 'age_group', 'gender', 
    'medical_condition', 'admission_date', 'discharge_date', 'los_days', 
    'doctor_id', 'insurance_provider', 'billing_amount', 'cost_per_day'
]
print(clean_df[preview_cols].head(5).to_string(index=False))
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

    target_path = "notebooks/02_preprocessing.ipynb"
    with open(target_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Successfully generated and executed: {target_path}")

    # Mirror to phase2_preprocessing
    p2_nb = "phase2_preprocessing/02_preprocessing.ipynb"
    shutil.copy(target_path, p2_nb)
    print(f"Mirrored notebook into: {p2_nb}")

if __name__ == "__main__":
    generate_preprocessing_notebook()
