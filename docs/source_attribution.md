# Data Source Attribution & Provenance

## 1. Dataset Overview
* **Dataset Title**: Healthcare Dataset
* **Source Platform**: Kaggle
* **Publisher / Author**: prasad22
* **Original URL**: [https://www.kaggle.com/datasets/prasad22/healthcare-dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset)
* **License**: [Insert Dataset License Here - e.g., CC0 1.0 Universal / Open Database License (ODbL)]
* **Access Date**: November 11, 2026
* **Local Ingestion Path**: `data/raw/healthcare_dataset.csv`
* **File Format**: Comma-Separated Values (CSV), UTF-8 encoded

---

## 2. Nature of Data & Synthetic Data Statement
**Notice**: This dataset contains entirely **synthetic** healthcare records. 
* All patient names, physician names, medical facilities, room numbers, billing figures, and clinical event timelines were artificially generated for demonstration, research, and benchmarking purposes.
* No data represents real human patients, identifiable living individuals, clinical malpractice, or proprietary hospital operations.
* Any resemblance between the synthetic patient/doctor identities and real persons or entities is purely coincidental.

---

## 3. Data Integrity & Ingestion Protocol
* **Read-Only Raw Policy**: The original file `data/raw/healthcare_dataset.csv` is maintained in an immutable, read-only status.
* **Downstream Reproducibility**: All transformations, cleaning passes, canonical column derivations, and pseudonymization routines are executed via versioned code and saved to `data/processed/` without altering or overwriting the raw source file.
* **Direct Identifiers**: While synthetic, direct identifier fields (`Name`, `Doctor`) are immediately pseudonymized or purged in downstream stages to demonstrate strict compliance with HIPAA and healthcare data privacy best practices.

