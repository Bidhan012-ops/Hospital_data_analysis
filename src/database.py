"""
SQLite Database & Storage Management for Hospital Analytics Portal
Provides persistent storage, schema validation, and dataset management for hospital admissions.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join("data", "hospital_analytics.db")

# Required column schemas
RAW_REQUIRED_COLUMNS = {
    "age", "gender", "medical_condition", "date_of_admission", 
    "discharge_date", "billing_amount", "admission_type"
}

CANONICAL_REQUIRED_COLUMNS = {
    "admission_id", "patient_key", "age", "gender", "medical_condition",
    "admission_date", "discharge_date", "los_days", "billing_amount"
}

def get_db_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initializes database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Metadata table for tracking uploaded datasets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT NOT NULL,
        source_type TEXT NOT NULL,
        row_count INTEGER NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def save_clean_dataset_to_db(df: pd.DataFrame, dataset_name: str = "default_processed_dataset"):
    """Saves or updates a processed dataset in the SQLite database."""
    init_database()
    conn = get_db_connection()
    
    # Save dataframe to 'admissions' table
    df_to_save = df.copy()
    if "admission_date" in df_to_save.columns:
        df_to_save["admission_date"] = df_to_save["admission_date"].astype(str)
    if "discharge_date" in df_to_save.columns:
        df_to_save["discharge_date"] = df_to_save["discharge_date"].astype(str)
        
    df_to_save.to_sql("admissions", conn, if_exists="replace", index=False)
    
    # Update registry
    cursor = conn.cursor()
    cursor.execute("UPDATE dataset_registry SET is_active = 0")
    cursor.execute("""
    INSERT INTO dataset_registry (dataset_name, source_type, row_count, is_active)
    VALUES (?, ?, ?, 1)
    """, (dataset_name, "canonical", len(df)))
    
    conn.commit()
    conn.close()
    print(f"[DB] Successfully stored {len(df):,} records into SQLite ({DB_PATH}).")

def load_active_dataset_from_db() -> pd.DataFrame:
    """Loads the active dataset from SQLite."""
    init_database()
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT * FROM admissions", conn)
        conn.close()
        if "admission_date" in df.columns:
            df["admission_date"] = pd.to_datetime(df["admission_date"])
        if "discharge_date" in df.columns:
            df["discharge_date"] = pd.to_datetime(df["discharge_date"])
        return df
    except Exception as e:
        conn.close()
        print(f"[DB WARN] Could not load from DB: {e}. Falling back to CSV.")
        return None

def validate_uploaded_csv(df: pd.DataFrame) -> tuple[bool, str, str]:
    """
    Validates uploaded CSV columns against required healthcare schema.
    Returns:
        (is_valid: bool, schema_type: 'raw' | 'canonical' | 'invalid', error_message: str)
    """
    # Normalize column names: lower case, strip spaces, replace spaces/hyphens with underscores
    normalized_cols = {col.strip().lower().replace(" ", "_").replace("-", "_"): col for col in df.columns}
    norm_set = set(normalized_cols.keys())
    
    # Check if canonical format
    if CANONICAL_REQUIRED_COLUMNS.issubset(norm_set):
        return True, "canonical", ""
        
    # Check if raw format
    if RAW_REQUIRED_COLUMNS.issubset(norm_set):
        return True, "raw", ""
        
    # Missing columns identification
    missing_raw = RAW_REQUIRED_COLUMNS - norm_set
    missing_canon = CANONICAL_REQUIRED_COLUMNS - norm_set
    
    # Format readable error message
    missing_display = sorted(list(missing_raw))
    err_msg = (
        f"Missing required healthcare columns: "
        f"{', '.join([col.replace('_', ' ').title() for col in missing_display])}."
    )
    return False, "invalid", err_msg

if __name__ == "__main__":
    init_database()
    csv_path = os.path.join("data", "processed", "hospital_clean.csv")
    if os.path.exists(csv_path):
        df_clean = pd.read_csv(csv_path)
        save_clean_dataset_to_db(df_clean)
        loaded = load_active_dataset_from_db()
        print(f"Verified SQLite load: {loaded.shape}")
