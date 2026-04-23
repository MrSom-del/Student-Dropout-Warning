from app import app
from extensions import db
from models.student_model import Student
from services.prediction_service import predict_student_dropout


EXAMPLE_STUDENTS = [
    {
        # Low-risk example
        "code_module": 1,
        "code_presentation": 1,
        "gender": 0,
        "region": 3,
        "highest_education": 2,
        "imd_band": 4,
        "age_band": 1,
        "num_of_prev_attempts": 0,
        "studied_credits": 60,
        "disability": 0,
        "total_clicks": 1500,
        "active_days": 70,
        "unique_resources": 45,
        "num_forum": 5,
        "num_quiz": 3,
        "avg_score": 85.0,
        "num_assess_attempted": 6,
        "total_weight": 100,
        "module_presentation_length": 240,
    },
    {
        # Medium-risk example
        "code_module": 1,
        "code_presentation": 1,
        "gender": 1,
        "region": 2,
        "highest_education": 1,
        "imd_band": 3,
        "age_band": 1,
        "num_of_prev_attempts": 1,
        "studied_credits": 60,
        "disability": 0,
        "total_clicks": 700,
        "active_days": 35,
        "unique_resources": 30,
        "num_forum": 4,
        "num_quiz": 2,
        "avg_score": 60.0,
        "num_assess_attempted": 5,
        "total_weight": 100,
        "module_presentation_length": 240,
    },
    {
        # High-risk example
        "code_module": 1,
        "code_presentation": 1,
        "gender": 0,
        "region": 1,
        "highest_education": 0,
        "imd_band": 2,
        "age_band": 2,
        "num_of_prev_attempts": 2,
        "studied_credits": 30,
        "disability": 0,
        "total_clicks": 200,
        "active_days": 10,
        "unique_resources": 10,
        "num_forum": 1,
        "num_quiz": 1,
        "avg_score": 35.0,
        "num_assess_attempted": 2,
        "total_weight": 100,
        "module_presentation_length": 240,
    },
]


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        for data in EXAMPLE_STUDENTS:
            prob, risk = predict_student_dropout(data)

            student = Student(
                **data,
                dropout_probability=prob,
                risk_level=risk,
            )

            db.session.add(student)

        db.session.commit()
        print("Seeded example students into the database.")

