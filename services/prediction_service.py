import joblib
import pandas as pd
try:
    import shap
except ModuleNotFoundError:
    shap = None

model = joblib.load("model/lightgbm_dropout_model.pkl")

feature_columns = [
"code_module",
"code_presentation",
"gender",
"region",
"highest_education",
"imd_band",
"age_band",
"num_of_prev_attempts",
"studied_credits",
"disability",
"total_clicks",
"active_days",
"unique_resources",
"num_forum",
"num_quiz",
"avg_score",
"num_assess_attempted",
"total_weight",
"module_presentation_length"
]

explainer = shap.TreeExplainer(model) if shap is not None else None

# Share of final probability from the trained model vs. an engagement heuristic.
# Higher engagement weight gives active_days / clicks / forum / quiz more influence
# without retraining the LightGBM model.
MODEL_WEIGHT = 0.52
ENGAGEMENT_WEIGHT = 1.0 - MODEL_WEIGHT

# Probability cutoffs used to map blended probability to risk bands.
# The previous values were too low and classified most students as HIGH.
RISK_HIGH_THRESHOLD = 0.55
RISK_MEDIUM_THRESHOLD = 0.30

# When ranking “top factors” for teachers, gently down-rank avg_score and up-rank
# activity signals so explanations match how strongly engagement affects the blend.
EXPLANATION_DISPLAY_WEIGHT = {
    "avg_score": 0.82,
    "active_days": 1.28,
    "total_clicks": 1.28,
    "unique_resources": 1.18,
    "num_forum": 1.15,
    "num_quiz": 1.12,
    "num_assess_attempted": 1.05,
}


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def engagement_dropout_prior(data: dict) -> float:
    """
    Heuristic dropout tendency (0–1) from activity and participation.
    Low activity → higher value. Independent of the ML model; used only in the blend.
    """
    ad = float(data.get("active_days") or 0)
    tc = float(data.get("total_clicks") or 0)
    ur = float(data.get("unique_resources") or 0)
    nf = float(data.get("num_forum") or 0)
    nq = float(data.get("num_quiz") or 0)

    ad_n = _clip01(ad / 100.0)
    tc_n = _clip01(tc / 2500.0)
    ur_n = _clip01(ur / 60.0)
    nf_n = _clip01(nf / 20.0)
    nq_n = _clip01(nq / 15.0)

    engagement = (
        0.30 * ad_n
        + 0.30 * tc_n
        + 0.15 * ur_n
        + 0.15 * nf_n
        + 0.10 * nq_n
    )
    return _clip01(1.0 - engagement)


def predict_student_dropout(data):

    input_df = pd.DataFrame([data])
    input_df = input_df[feature_columns]

    prob_model = float(model.predict_proba(input_df)[0][1])
    prob_engagement = engagement_dropout_prior(data)
    prob = MODEL_WEIGHT * prob_model + ENGAGEMENT_WEIGHT * prob_engagement

    if prob >= RISK_HIGH_THRESHOLD:
        risk = "HIGH"
    elif prob >= RISK_MEDIUM_THRESHOLD:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return prob, risk


def explain_prediction(data):
    if explainer is None:
        return fallback_explanation(data)

    try:
        input_df = pd.DataFrame([data])
        input_df = input_df[feature_columns]

        shap_values = explainer.shap_values(input_df)

        # Handle SHAP format differences
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        contributions = {}

        for i, feature in enumerate(feature_columns):
            contributions[feature] = float(shap_values[0][i])

        # Sort by adjusted importance so teachers see engagement features more often
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]) * EXPLANATION_DISPLAY_WEIGHT.get(x[0], 1.0),
            reverse=True,
        )

        # Take top 5
        top_factors = sorted_features[:5]

        result = []

        for feature, value in top_factors:
            result.append({
                "feature": feature,
                "impact": value
            })

        return result
    except Exception:
        # Keep prediction endpoint resilient in environments where SHAP
        # dependencies fail at runtime (common on lightweight deployments).
        return fallback_explanation(data)


def fallback_explanation(data):
    baseline = {
        "active_days": 35.0,
        "total_clicks": 700.0,
        "unique_resources": 30.0,
        "num_forum": 4.0,
        "num_quiz": 2.0,
        "avg_score": 60.0,
        "num_assess_attempted": 5.0,
    }
    direction = {
        # Lower engagement and lower score increase risk.
        "active_days": -1.0,
        "total_clicks": -1.0,
        "unique_resources": -1.0,
        "num_forum": -1.0,
        "num_quiz": -1.0,
        "avg_score": -1.0,
        "num_assess_attempted": -1.0,
    }

    impacts = []
    for feature, base_value in baseline.items():
        value = float(data.get(feature) or 0.0)
        relative = (value - base_value) / max(base_value, 1.0)
        impact = direction[feature] * relative
        impacts.append((feature, impact))

    top_factors = sorted(
        impacts,
        key=lambda x: abs(x[1]) * EXPLANATION_DISPLAY_WEIGHT.get(x[0], 1.0),
        reverse=True,
    )[:5]

    return [{"feature": feature, "impact": float(impact)} for feature, impact in top_factors]