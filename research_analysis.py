"""
research_analysis.py
====================
Standalone script for MediGuide research paper.
Generates:
  1. Full synthetic dataset (870 rows) -> CSV
  2. Feature documentation (console)
  3. Train/test split (80:20, random_state=42)
  4. Random Forest evaluation metrics
  5. Logistic Regression evaluation metrics
  6. RF vs LR comparison table
  7. 5 realistic prediction examples

NOTE: This script does NOT modify any existing project files.
Run from the project root: python research_analysis.py
"""

import numpy as np
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# ─────────────────────────────────────────────
# 1. REPRODUCE SYNTHETIC DATASET (same logic as ml_classifier.py)
# ─────────────────────────────────────────────
np.random.seed(42)   # Fixed seed for reproducibility

rows = []

# MINOR (350 samples)
for _ in range(350):
    severity    = np.random.uniform(1, 4)
    red_flags   = 0
    duration_sc = np.random.uniform(0, 4)
    criticality = np.random.uniform(1, 6)
    score = severity*0.40 + red_flags*10*0.30 + duration_sc*0.20 + criticality*0.10
    rows.append({
        "severity": round(severity, 4),
        "red_flag": int(red_flags),
        "duration_score": round(duration_sc, 4),
        "criticality": round(criticality, 4),
        "urgency_score": round(score, 4),
        "label": 0,
        "triage_class": "MINOR"
    })

# CONSULTATION (270 samples)
for _ in range(270):
    severity    = np.random.uniform(3, 7)
    red_flags   = np.random.choice([0, 1], p=[0.6, 0.4])
    duration_sc = np.random.uniform(2, 8)
    criticality = np.random.uniform(3, 8)
    score = severity*0.40 + red_flags*10*0.30 + duration_sc*0.20 + criticality*0.10
    rows.append({
        "severity": round(severity, 4),
        "red_flag": int(red_flags),
        "duration_score": round(duration_sc, 4),
        "criticality": round(criticality, 4),
        "urgency_score": round(score, 4),
        "label": 1,
        "triage_class": "CONSULTATION"
    })

# EMERGENCY (250 samples)
for _ in range(250):
    severity    = np.random.uniform(6, 10)
    red_flags   = np.random.choice([0, 1], p=[0.2, 0.8])
    duration_sc = np.random.uniform(3, 10)
    criticality = np.random.uniform(6, 10)
    score = severity*0.40 + red_flags*10*0.30 + duration_sc*0.20 + criticality*0.10
    rows.append({
        "severity": round(severity, 4),
        "red_flag": int(red_flags),
        "duration_score": round(duration_sc, 4),
        "criticality": round(criticality, 4),
        "urgency_score": round(score, 4),
        "label": 2,
        "triage_class": "EMERGENCY"
    })

df = pd.DataFrame(rows)

# Save full dataset CSV
csv_path = "research_dataset.csv"
df.to_csv(csv_path, index=False)
print(f"\n{'='*60}")
print(f"DATASET EXPORTED -> {csv_path}  ({len(df)} rows)")
print(f"{'='*60}")
print(f"\nClass distribution:")
print(df["triage_class"].value_counts().to_string())

print(f"\nFirst 10 rows (preview):")
print(df.head(10).to_string(index=False))

# ─────────────────────────────────────────────
# 2. FEATURE DOCUMENTATION
# ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("FEATURE DOCUMENTATION")
print(f"{'='*60}")
features_info = [
    {
        "Feature":        "severity",
        "Type":           "Numeric (float)",
        "Range":          "1.0 – 10.0",
        "Derivation":     "Patient-reported via NLP (1-10 scale or keyword mapping). Minor: 1-4, Moderate: 4-7, Severe: 7-10",
        "Weight in Score":"40%"
    },
    {
        "Feature":        "red_flag",
        "Type":           "Binary (int)",
        "Range":          "0 or 1",
        "Derivation":     "1 if patient answers 'yes' to follow-up red-flag question (e.g. chest pain, difficulty breathing). 0 otherwise.",
        "Weight in Score":"30%  (multiplied by 10 before weighting)"
    },
    {
        "Feature":        "duration_score",
        "Type":           "Numeric (float)",
        "Range":          "0.0 – 10.0",
        "Derivation":     "Normalised from raw duration hours: min(10, duration_hours / 336 * 10). 336h = 2 weeks cap.",
        "Weight in Score":"20%"
    },
    {
        "Feature":        "criticality",
        "Type":           "Numeric (float)",
        "Range":          "1.0 – 10.0",
        "Derivation":     "Looked up from symptoms.json for the matched symptom key (pre-assigned expert score).",
        "Weight in Score":"10%"
    },
    {
        "Feature":        "urgency_score  [MODEL INPUT]",
        "Type":           "Numeric (float)",
        "Range":          "~0.0 – 13.0",
        "Derivation":     "severity×0.40 + red_flag×10×0.30 + duration_score×0.20 + criticality×0.10",
        "Weight in Score":"N/A — this IS the single feature fed to the model"
    },
]
feat_df = pd.DataFrame(features_info)
print(feat_df.to_string(index=False))

print("\nLabel Mapping:")
print("  0 -> MINOR        (urgency_score < 3.5)")
print("  1 -> CONSULTATION (urgency_score 3.5 – 6.5)")
print("  2 -> EMERGENCY    (urgency_score > 6.5)")

# ─────────────────────────────────────────────
# 3. TRAIN / TEST SPLIT (80:20, random_state=42)
# ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("TRAIN / TEST SPLIT")
print(f"{'='*60}")

X = df[["urgency_score"]].values
y = df["label"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print(f"  Total samples  : {len(df)}")
print(f"  Training set   : {len(X_train)} samples (80%)")
print(f"  Test set       : {len(X_test)} samples (20%)")
print(f"  random_state   : 42")
print(f"  Stratified     : Yes (class proportions preserved)")

# ─────────────────────────────────────────────
# 4. RANDOM FOREST — TRAIN & EVALUATE
# ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("RANDOM FOREST CLASSIFIER — EVALUATION")
print(f"{'='*60}")

rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)
rf.fit(X_train_sc, y_train)
y_pred_rf = rf.predict(X_test_sc)

rf_acc  = accuracy_score(y_test, y_pred_rf)
rf_prec = precision_score(y_test, y_pred_rf, average='weighted')
rf_rec  = recall_score(y_test, y_pred_rf, average='weighted')
rf_f1   = f1_score(y_test, y_pred_rf, average='weighted')
rf_cm   = confusion_matrix(y_test, y_pred_rf)

print(f"  Accuracy           : {rf_acc:.4f} ({rf_acc*100:.2f}%)")
print(f"  Precision (weighted): {rf_prec:.4f}")
print(f"  Recall    (weighted): {rf_rec:.4f}")
print(f"  F1-score  (weighted): {rf_f1:.4f}")
print(f"\n  Confusion Matrix (rows=Actual, cols=Predicted):")
print(f"                MINOR  CONSULT  EMERGENCY")
labels_names = ["MINOR", "CONSULT", "EMERG"]
for i, row in enumerate(rf_cm):
    print(f"  {labels_names[i]:12s}  {row[0]:5d}  {row[1]:7d}  {row[2]:9d}")

print(f"\n  Full Classification Report:")
print(classification_report(y_test, y_pred_rf,
      target_names=["MINOR", "CONSULTATION", "EMERGENCY"]))

# ─────────────────────────────────────────────
# 5. LOGISTIC REGRESSION — TRAIN & EVALUATE
# ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("LOGISTIC REGRESSION CLASSIFIER — EVALUATION")
print(f"{'='*60}")

lr = LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight='balanced'
)
lr.fit(X_train_sc, y_train)
y_pred_lr = lr.predict(X_test_sc)

lr_acc  = accuracy_score(y_test, y_pred_lr)
lr_prec = precision_score(y_test, y_pred_lr, average='weighted')
lr_rec  = recall_score(y_test, y_pred_lr, average='weighted')
lr_f1   = f1_score(y_test, y_pred_lr, average='weighted')
lr_cm   = confusion_matrix(y_test, y_pred_lr)

print(f"  Accuracy           : {lr_acc:.4f} ({lr_acc*100:.2f}%)")
print(f"  Precision (weighted): {lr_prec:.4f}")
print(f"  Recall    (weighted): {lr_rec:.4f}")
print(f"  F1-score  (weighted): {lr_f1:.4f}")
print(f"\n  Confusion Matrix (rows=Actual, cols=Predicted):")
print(f"                MINOR  CONSULT  EMERGENCY")
for i, row in enumerate(lr_cm):
    print(f"  {labels_names[i]:12s}  {row[0]:5d}  {row[1]:7d}  {row[2]:9d}")

print(f"\n  Full Classification Report:")
print(classification_report(y_test, y_pred_lr,
      target_names=["MINOR", "CONSULTATION", "EMERGENCY"]))

# ─────────────────────────────────────────────
# 6. COMPARISON TABLE
# ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("MODEL COMPARISON: Random Forest vs Logistic Regression")
print(f"{'='*60}")
comp_df = pd.DataFrame({
    "Metric":              ["Accuracy", "Precision (weighted)", "Recall (weighted)", "F1-Score (weighted)"],
    "Random Forest":       [f"{rf_acc:.4f}", f"{rf_prec:.4f}", f"{rf_rec:.4f}", f"{rf_f1:.4f}"],
    "Logistic Regression": [f"{lr_acc:.4f}", f"{lr_prec:.4f}", f"{lr_rec:.4f}", f"{lr_f1:.4f}"],
    "Better Model":        [
        "RF" if rf_acc  > lr_acc  else "LR",
        "RF" if rf_prec > lr_prec else "LR",
        "RF" if rf_rec  > lr_rec  else "LR",
        "RF" if rf_f1   > lr_f1   else "LR",
    ]
})
print(comp_df.to_string(index=False))

# ─────────────────────────────────────────────
# 7. REALISTIC PREDICTION EXAMPLES (5 cases)
# ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("SAMPLE PREDICTION EXAMPLES (5 realistic cases)")
print(f"{'='*60}")

label_map = {0: "MINOR", 1: "CONSULTATION", 2: "EMERGENCY"}

examples = [
    # (description, severity, red_flag, duration_hours, criticality)
    ("Mild headache, no red flags, 6 hours",          2.0, 0, 6,   4.0),
    ("Moderate back pain, no red flags, 3 days",      5.0, 0, 72,  5.0),
    ("Chest pain, has red flags, 2 hours",            8.0, 1, 2,   9.0),
    ("Fever + cough, red flag, 2 days",               6.0, 1, 48,  7.0),
    ("Minor skin rash, no red flags, 1 week",         3.0, 0, 168, 3.0),
]

example_rows = []
for desc, sev, rf_flag, dur_hrs, crit in examples:
    dur_sc = min(10.0, (dur_hrs / 336.0) * 10.0)
    u_score = sev*0.40 + rf_flag*10*0.30 + dur_sc*0.20 + crit*0.10
    feat = np.array([[u_score]])
    feat_sc = scaler.transform(feat)
    pred_rf = rf.predict(feat_sc)[0]
    example_rows.append({
        "Description":     desc,
        "Severity (1-10)": sev,
        "Red Flag":        rf_flag,
        "Duration (hrs)":  dur_hrs,
        "Dur Score":       round(dur_sc, 3),
        "Criticality":     crit,
        "Urgency Score":   round(u_score, 4),
        "RF Prediction":   label_map[pred_rf],
    })

ex_df = pd.DataFrame(example_rows)
print(ex_df.to_string(index=False))

print(f"\n{'='*60}")
print(f"DONE.  Full dataset saved to: {os.path.abspath(csv_path)}")
print(f"{'='*60}\n")
