from flask import Blueprint, jsonify, render_template
from models.student_model import Student
from services.prediction_service import explain_prediction, feature_columns

student_bp = Blueprint("students", __name__)

# Get all students
@student_bp.route("/students", methods=["GET"])
def get_students():

    students = Student.query.all()

    result = []

    for s in students:
        result.append({
            "id": s.id,
            "dropout_probability": s.dropout_probability,
            "risk_level": s.risk_level
        })

    return jsonify(result)


# Get a single student
@student_bp.route("/students/<int:id>", methods=["GET"])
def get_student(id):

    student = Student.query.get_or_404(id)

    return jsonify({
        "id": student.id,
        "dropout_probability": student.dropout_probability,
        "risk_level": student.risk_level
    })


# Get high risk students
@student_bp.route("/high-risk", methods=["GET"])
def high_risk_students():

    students = Student.query.filter_by(risk_level="HIGH").all()

    result = []

    for s in students:
        result.append({
            "id": s.id,
            "dropout_probability": s.dropout_probability
        })

    return jsonify(result)
@student_bp.route("/analytics", methods=["GET"])
def analytics():

    total = Student.query.count()

    high = Student.query.filter_by(risk_level="HIGH").count()
    medium = Student.query.filter_by(risk_level="MEDIUM").count()
    low = Student.query.filter_by(risk_level="LOW").count()

    return {
        "total_students": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low
    }


@student_bp.route("/students/<int:id>/profile", methods=["GET"])
def student_profile(id):

    student = Student.query.get_or_404(id)

    data = {col: getattr(student, col) for col in feature_columns}
    top_factors = explain_prediction(data)

    feature_labels = {
        "code_module": "Module",
        "code_presentation": "Presentation",
        "gender": "Gender",
        "region": "Region",
        "highest_education": "Highest Education",
        "imd_band": "Deprivation Index Band",
        "age_band": "Age Band",
        "num_of_prev_attempts": "Previous Attempts",
        "studied_credits": "Studied Credits",
        "disability": "Disability",
        "total_clicks": "Total Learning Interactions",
        "active_days": "Active Days",
        "unique_resources": "Unique Resources Accessed",
        "num_forum": "Forum Posts",
        "num_quiz": "Quizzes Taken",
        "avg_score": "Average Score",
        "num_assess_attempted": "Assessments Attempted",
        "total_weight": "Total Assessment Weight",
        "module_presentation_length": "Module Length (Days)",
    }

    if student.risk_level == "HIGH":
        actions = [
            "Assign a mentor for weekly check-ins",
            "Encourage participation in forums and group discussions",
            "Send reminders for upcoming assessments and deadlines",
        ]
    elif student.risk_level == "MEDIUM":
        actions = [
            "Monitor engagement over the next few weeks",
            "Provide optional study group or tutoring sessions",
            "Share personalized feedback on recent assessments",
        ]
    else:
        actions = [
            "Continue current support and feedback cadence",
            "Offer opportunities for advanced/extension activities",
        ]

    return render_template(
        "student_profile.html",
        student=student,
        top_factors=top_factors,
        actions=actions,
        feature_labels=feature_labels,
    )