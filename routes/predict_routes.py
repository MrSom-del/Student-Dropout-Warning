from flask import Blueprint, request, jsonify
from services.prediction_service import predict_student_dropout, explain_prediction
from models.student_model import Student
from extensions import db

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    prob, risk = predict_student_dropout(data)

    return jsonify({
        "dropout_probability": float(prob),
        "risk_level": risk
    })


@predict_bp.route("/explain", methods=["POST"])
def explain():

    data = request.get_json()

    prob, risk = predict_student_dropout(data)
    explanation = explain_prediction(data)

    # Save this prediction to the database so it appears in analytics/history
    student = Student(
        **data,
        dropout_probability=prob,
        risk_level=risk,
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "dropout_probability": float(prob),
        "risk_level": risk,
        "top_risk_factors": explanation
    })