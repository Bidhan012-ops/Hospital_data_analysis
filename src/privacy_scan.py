"""
Privacy Scan Script (src/privacy_scan.py)
-----------------------------------------
Reads direct identifiers (Name, Doctor) from data/raw/healthcare_dataset.csv
and scans all deliverables across notebooks/, outputs/, docs/, powerbi/, and
phase directories to verify that no direct identifier is leaked.

Returns exit code 0 if all clean (PASS), or 1 if any identifier is found (FAIL).
"""

import os
import re
import sys
import pandas as pd
from pathlib import Path


def clean_text(text: str) -> str:
    """Normalize text by removing non-alphanumeric characters and extra spaces."""
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text).lower()


def load_raw_identifiers(raw_csv_path: str = "data/raw/healthcare_dataset.csv"):
    if not os.path.exists(raw_csv_path):
        print(f"[ERROR] Raw dataset not found at {raw_csv_path}")
        sys.exit(1)

    df = pd.read_csv(raw_csv_path, usecols=["Name", "Doctor"])
    names = df["Name"].dropna().astype(str).tolist()
    doctors = df["Doctor"].dropna().astype(str).tolist()

    clean_identifiers = set()
    raw_lookup = {}
    for item in names + doctors:
        norm = " ".join(clean_text(item).split())
        if norm and len(norm) >= 4 and len(norm.split()) >= 2:
            clean_identifiers.add(norm)
            raw_lookup[norm] = item.strip()

    return clean_identifiers, raw_lookup


def scan_file(file_path: Path, identifiers: set, raw_lookup: dict):
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"[WARN] Could not read {file_path}: {e}")
        return violations

    cleaned = " ".join(clean_text(content).split())
    tokens = cleaned.split()
    total_tokens = len(tokens)

    # Check 2-grams, 3-grams, and 4-grams against identifier set
    for n in (2, 3, 4):
        for i in range(total_tokens - n + 1):
            ngram = " ".join(tokens[i : i + n])
            if ngram in identifiers:
                violations.append((file_path, raw_lookup.get(ngram, ngram)))

    return violations


def run_privacy_scan(target_dirs=None):
    if target_dirs is None:
        target_dirs = ["notebooks", "outputs", "docs", "powerbi", "phase1_foundation"]

    raw_csv = "data/raw/healthcare_dataset.csv"
    print("=" * 70)
    print("AUTOMATED PRIVACY AUDIT & DIRECT IDENTIFIER LEAK SCAN")
    print("=" * 70)
    print(f"Loading raw identifiers from: {raw_csv}")

    identifiers, raw_lookup = load_raw_identifiers(raw_csv)
    print(f"Total unique multi-word direct identifiers indexed: {len(identifiers):,}")

    scanned_files = []
    all_violations = []

    # File extensions to scan
    scan_exts = {".md", ".csv", ".ipynb", ".py", ".txt", ".json", ".html", ".xml", ".sql"}

    for t_dir in target_dirs:
        dir_path = Path(t_dir)
        if not dir_path.exists():
            continue
        for root, _, files in os.walk(dir_path):
            for file in files:
                p = Path(root) / file
                if p.suffix.lower() in scan_exts:
                    scanned_files.append(p)
                    viols = scan_file(p, identifiers, raw_lookup)
                    if viols:
                        all_violations.extend(viols)

    print(f"Total files scanned across target directories: {len(scanned_files)}")
    print("-" * 70)

    if not all_violations:
        print("[RESULT] PASS: Zero direct personal identifiers found.")
        print("All scanned notebooks, outputs, docs, and powerbi files are clean.")
        print("=" * 70)
        return True, len(scanned_files), len(identifiers), []
    else:
        print(f"[RESULT] FAIL: Found {len(all_violations)} privacy violations!")
        for file_path, name in set(all_violations):
            print(f"  - Leaked Identifier: '{name}' in file: {file_path}")
        print("=" * 70)
        return False, len(scanned_files), len(identifiers), all_violations


if __name__ == "__main__":
    passed, n_files, n_ids, viols = run_privacy_scan()
    sys.exit(0 if passed else 1)

