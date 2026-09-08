import joblib
import pandas as pd
from pathlib import Path


# ============================================================
# MODEL LOADING
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "backend"
    / "ML"
    / "cryptoattrib_rf_model.pkl"
)
model = joblib.load(MODEL_PATH)


# ============================================================
# RISK PREDICTION
# ============================================================

def predict_risk(features: dict):
    """
    Predict illicit-wallet risk.

    Parameters
    ----------
    features : dict
        Dictionary containing the 55 features expected
        by the trained Random Forest model.

    Returns
    -------
    dict
        Prediction, risk score and risk level.
    """

    # Convert dictionary to DataFrame
    X = pd.DataFrame([features])

    # Make sure feature order matches training
    X = X[model.feature_names_in_]

    # Prediction
    prediction = int(model.predict(X)[0])

    # Probability of illicit class
    illicit_probability = float(
        model.predict_proba(X)[0][1]
    )

    # Risk level
    if illicit_probability >= 0.75:
        risk_level = "HIGH"

    elif illicit_probability >= 0.40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    prediction_label = (
        "ILLICIT"
        if prediction == 1
        else "LICIT"
    )

    return {
        "prediction": prediction_label,
        "risk_score": round(illicit_probability, 4),
        "risk_percentage": round(
            illicit_probability * 100,
            2
        ),
        "risk_level": risk_level
    }