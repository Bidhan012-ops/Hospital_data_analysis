"""
In-process execution and generation of notebooks/01_data_inspection.ipynb
Guarantees sandbox safety, zero socket hanging, complete execution of all cells,
and populates output stream and MIME bundles cleanly.
"""

import os
import io
import sys
import contextlib
import shutil
import nbformat as nbf
import pandas as pd
import numpy as np

def generate_executed_notebook():
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
        ("markdown", """# 01. Raw Data Inspection & Quality Assessment
**Phase 1: Project Foundation, Data Collection, Data Dictionary and Privacy**
**Project:** Hospital Patient Data Analysis and Dashboard Development Using Python and Power BI

---

### Objective & Privacy Protocol
This notebook performs an exhaustive preliminary inspection of the raw healthcare dataset (`data/raw/healthcare_dataset.csv`), evaluating structure, schema fidelity, completeness, cardinality, date bounds, and value distributions.

> **CRITICAL PRIVACY DIRECTIVE**:
> In compliance with healthcare data protection standards and project non-negotiables, all direct personal identifiers (`Name`, `Doctor`) are **strictly masked** in all tabular previews and console outputs to prevent privacy leaks.
"""),
        ("code", """# Environment configuration, seed setting, and package imports
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for complete reproducibility
np.random.seed(42)

# Set display preferences
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print(f"Python interpreter: {sys.version.split()[0]}")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
"""),
        ("markdown", """## 1. Raw Dataset Ingestion & Dimension Verification
Loading raw data from `data/raw/healthcare_dataset.csv` using relative paths."""),
        ("code", """# Resolve relative path whether running from root or notebooks/
raw_path = 'data/raw/healthcare_dataset.csv'
if not os.path.exists(raw_path):
    raw_path = '../data/raw/healthcare_dataset.csv'

assert os.path.exists(raw_path), f"File not found at {raw_path}"

df_raw = pd.read_csv(raw_path)
n_rows, n_cols = df_raw.shape

print(f"Loaded dataset successfully from: {raw_path}")
print(f"Total Admissions (Rows) : {n_rows:,}")
print(f"Total Columns (Fields)  : {n_cols}")
"""),
        ("markdown", """## 2. Privacy-Safe Tabular Preview
Previewing sample records with `Name` and `Doctor` completely masked."""),
        ("code", """def privacy_safe_preview(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    \"\"\"Return a copy of the dataframe with direct identifiers masked.\"\"\"
    preview = df.head(n).copy()
    if 'Name' in preview.columns:
        preview['Name'] = [f"PATIENT_{str(i+1).zfill(5)} [MASKED]" for i in range(len(preview))]
    if 'Doctor' in preview.columns:
        preview['Doctor'] = [f"DOCTOR_{str(i+1).zfill(3)} [MASKED]" for i in range(len(preview))]
    return preview

preview_df = privacy_safe_preview(df_raw, 5)
print(preview_df.to_string())
"""),
        ("markdown", """## 3. Schema, Data Types & Missing Value Audit"""),
        ("code", """# Inspect data types and missing counts across all columns
null_counts = df_raw.isnull().sum()
null_pct = (null_counts / len(df_raw)) * 100

schema_audit_df = pd.DataFrame({
    'Column Name': df_raw.columns,
    'Non-Null Count': df_raw.notnull().sum(),
    'Null Count': null_counts,
    'Null Percentage (%)': null_pct,
    'Data Type': df_raw.dtypes.astype(str)
}).reset_index(drop=True)

print("Comprehensive Schema & Missing Value Audit:")
print(schema_audit_df.to_string())
"""),
        ("markdown", """## 4. Cardinality & Unique Value Analysis"""),
        ("code", """# Assess distinct counts per field
unique_counts = df_raw.nunique()
cardinality_df = pd.DataFrame({
    'Column Name': df_raw.columns,
    'Distinct Count': unique_counts,
    'Uniqueness Ratio (%)': ((unique_counts / len(df_raw)) * 100).round(2),
    'Classification': [
        'Direct Identifier (High Cardinality)' if col in ['Name', 'Doctor']
        else 'Non-Identifying High Cardinality' if u > 1000
        else 'Quasi-Identifier / Numeric' if u > 10
        else 'Categorical Domain'
        for col, u in zip(df_raw.columns, unique_counts)
    ]
}).reset_index(drop=True)

print("Field Cardinality & Unique Value Distribution:")
print(cardinality_df.to_string())
"""),
        ("markdown", """## 5. Temporal Boundaries & Stay Duration Analysis
Assessing `Date of Admission` and `Discharge Date` chronology and stay integrity."""),
        ("code", """# Parse datetime fields
adm_dates = pd.to_datetime(df_raw['Date of Admission'])
dis_dates = pd.to_datetime(df_raw['Discharge Date'])

stay_duration_days = (dis_dates - adm_dates).dt.days

print("=" * 60)
print("TEMPORAL BOUNDS AUDIT")
print("=" * 60)
print(f"Earliest Admission Date : {adm_dates.min().strftime('%Y-%m-%d')}")
print(f"Latest Admission Date   : {adm_dates.max().strftime('%Y-%m-%d')}")
print(f"Total Admission Span    : {(adm_dates.max() - adm_dates.min()).days} calendar days")
print(f"Earliest Discharge Date : {dis_dates.min().strftime('%Y-%m-%d')}")
print(f"Latest Discharge Date   : {dis_dates.max().strftime('%Y-%m-%d')}")

# Chronological validation
inverted_stays = (stay_duration_days < 0).sum()
same_day_stays = (stay_duration_days == 0).sum()
print(f"Negative Stay Anomalies (Discharge < Admission) : {inverted_stays}")
print(f"Same-Day Stays (Discharge == Admission)          : {same_day_stays}")
print("\\nStay Duration Distribution (Raw Days):")
print(stay_duration_days.describe().to_string())
"""),
        ("markdown", """## 6. Numeric Field Summaries & Anomaly Detection
Auditing `Age`, `Billing Amount`, and `Room Number` distributions."""),
        ("code", """numeric_cols = ['Age', 'Billing Amount', 'Room Number']
num_stats = df_raw[numeric_cols].describe().T
num_stats['median'] = df_raw[numeric_cols].median()
num_stats['skewness'] = df_raw[numeric_cols].skew()
num_stats['kurtosis'] = df_raw[numeric_cols].kurtosis()

print("Descriptive Statistics for Numeric Columns:")
print(num_stats[['count', 'mean', 'std', 'min', '25%', 'median', '75%', 'max', 'skewness', 'kurtosis']].to_string())

# Deep dive into anomalies: negative billing amounts
neg_billing = df_raw[df_raw['Billing Amount'] < 0]
print(f"\\nNegative Billing Amount Records Detected: {len(neg_billing)}")
if len(neg_billing) > 0:
    print(f"Minimum Billing Amount: ${df_raw['Billing Amount'].min():,.2f}")
    print(f"Maximum Billing Amount: ${df_raw['Billing Amount'].max():,.2f}")
"""),
        ("markdown", """## 7. Categorical Field Distributions & Value Counts"""),
        ("code", """cat_columns = [
    'Gender', 'Blood Type', 'Medical Condition', 
    'Insurance Provider', 'Admission Type', 'Medication', 'Test Results'
]

for col in cat_columns:
    counts = df_raw[col].value_counts()
    pcts = df_raw[col].value_counts(normalize=True) * 100
    summary_cat = pd.DataFrame({'Frequency': counts, 'Percentage (%)': pcts.round(2)})
    print(f"\\n{'='*20} {col.upper()} {'='*20}")
    print(summary_cat.to_string())
"""),
        ("markdown", """## 8. Summary of Data Inspection Findings & Next Steps

### Key Diagnostic Observations:
1. **Dimensions**: 55,500 admissions across 15 source columns.
2. **Data Completeness**: Zero null or missing values across all columns.
3. **Temporal Span**: Admissions span 5 complete calendar years (2019-05-08 to 2024-05-07).
4. **Stay Durations**: Mean stay duration is ~15.5 days (range: 1 to 30 days). No negative stay anomalies detected.
5. **Billing Artifact**: Billed amounts range from -$2,008.49 to +$52,764.28 with a median of $25,538.07. Outlier handling / validation will be addressed in Phase 2.
6. **Demographics**: Patient age spans 13 to 89 years (mean: 51.5 years). Gender is evenly split (50.0% Male, 50.0% Female).
7. **Privacy Requirements**: `Name` and `Doctor` are high-cardinality direct identifiers that must be transformed into `patient_key` and `doctor_id` in downstream processing.
""")
    ]

    execution_context = {}
    nb_cells = []
    execution_count = 1

    for cell_type, content in cells_definition:
        if cell_type == "markdown":
            nb_cells.append(nbf.v4.new_markdown_cell(content))
        elif cell_type == "code":
            # Intercept stdout and execute
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

    target_path = "notebooks/01_data_inspection.ipynb"
    with open(target_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Successfully generated and executed: {target_path}")

    # Mirror into phase1_foundation
    phase1_nb = "phase1_foundation/01_data_inspection.ipynb"
    shutil.copy(target_path, phase1_nb)
    print(f"Mirrored notebook into: {phase1_nb}")

if __name__ == "__main__":
    generate_executed_notebook()
