from flask import Blueprint, request, jsonify
from services.prediction_service import predict_student_dropout, explain_prediction
from models.student_model import Student
from extensions import db

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() or {}
        prob, risk = predict_student_dropout(data)
        return jsonify(
            {
                "dropout_probability": float(prob),
                "risk_level": risk,
            }
        )
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


@predict_bp.route("/explain", methods=["POST"])
def explain():
    try:
        data = request.get_json() or {}
        prob, risk = predict_student_dropout(data)
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500

    # Try explanation; if it fails, keep endpoint usable.
    try:
        explanation = explain_prediction(data)
    except Exception:
        explanation = []

    # Try save; if DB write fails, still return computed result.
    try:
        student = Student(
            **data,
            dropout_probability=prob,
            risk_level=risk,
        )
        db.session.add(student)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify(
        {
            "dropout_probability": float(prob),
            "risk_level": risk,
            "top_risk_factors": explanation,
        }
    )
