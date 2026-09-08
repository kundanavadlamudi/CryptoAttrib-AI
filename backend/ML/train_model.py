import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score
)


# ============================================================
# PATHS
# ============================================================

project_root = Path(__file__).resolve().parent.parent.parent

input_file = (
    project_root
    / "DATASET"
    / "wallet_level_dataset.csv"
)

model_file = (
    project_root
    / "backend"
    / "ML"
    / "cryptoattrib_rf_model.pkl"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("CRYPTOATTRIB AI - RANDOM FOREST TRAINING")
print("=" * 70)

print("\nLoading dataset...")
print(input_file)

df = pd.read_csv(input_file)

print(f"\nDataset shape: {df.shape}")
print(f"Total wallets: {len(df):,}")


# ============================================================
# PREPARE FEATURES AND TARGET
# ============================================================

# Address is an identifier, NOT an ML feature
X = df.drop(columns=["address", "class"])

# Convert:
# Class 1 = Illicit → 1
# Class 2 = Licit   → 0

y = (df["class"] == 1).astype(int)

print("\n" + "=" * 70)
print("DATASET PREPARATION")
print("=" * 70)

print(f"\nNumber of features: {X.shape[1]}")

print("\nTarget distribution:")

print(
    f"Illicit: {y.sum():,} "
    f"({y.mean() * 100:.2f}%)"
)

print(
    f"Licit: {(y == 0).sum():,} "
    f"({(y == 0).mean() * 100:.2f}%)"
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"\nTraining wallets: {len(X_train):,}")
print(f"Testing wallets:  {len(X_test):,}")

print("\nTraining class distribution:")
print(y_train.value_counts())

print("\nTesting class distribution:")
print(y_test.value_counts())


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

print("\n" + "=" * 70)
print("TRAINING RANDOM FOREST")
print("=" * 70)

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
    max_features="sqrt"
)

print("\nModel configuration:")
print("Algorithm       : Random Forest")
print("Trees           : 300")
print("Class weighting : balanced")
print("Max features    : sqrt")
print("Random state    : 42")

print("\nTraining model...")

model.fit(X_train, y_train)

print("Training complete! 🔥")


# ============================================================
# PREDICTIONS
# ============================================================

print("\n" + "=" * 70)
print("GENERATING PREDICTIONS")
print("=" * 70)

y_pred = model.predict(X_test)

# Probability of class 1 = illicit probability
y_probability = model.predict_proba(X_test)[:, 1]


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Licit", "Illicit"],
        digits=4
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

cm = confusion_matrix(y_test, y_pred)

print("\n                 Predicted")
print("                Licit  Illicit")
print(
    f"Actual Licit    {cm[0,0]:6d}  {cm[0,1]:7d}"
)
print(
    f"Actual Illicit  {cm[1,0]:6d}  {cm[1,1]:7d}"
)


# ============================================================
# ROC-AUC
# ============================================================

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

print("\n" + "=" * 70)
print("ROC-AUC")
print("=" * 70)

print(f"\nROC-AUC: {roc_auc:.4f}")


# ============================================================
# PR-AUC
# ============================================================

pr_auc = average_precision_score(
    y_test,
    y_probability
)

print("\n" + "=" * 70)
print("PR-AUC")
print("=" * 70)

print(f"\nPR-AUC: {pr_auc:.4f}")


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("TOP 15 FEATURE IMPORTANCES")
print("=" * 70)

feature_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print(
    feature_importance.head(15).to_string(
        index=False
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

print("\n" + "=" * 70)
print("SAVING MODEL")
print("=" * 70)

joblib.dump(
    model,
    model_file
)

print("\nModel saved successfully!")

print(model_file)

print("\n" + "=" * 70)
print("TRAINING FINISHED 🚀")
print("=" * 70)