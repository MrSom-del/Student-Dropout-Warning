"""Create demo teacher accounts. Run once: python seed_teachers.py"""

import os

from app import app
from extensions import db
from models.teacher_model import Teacher

DEMO_TEACHERS = [
    {
        "username": "teacher1",
        "password": "teacher123",
        "full_name": "Dr. A. Sharma",
        "school_name": "Demo College of Engineering",
    },
    {
        "username": "teacher2",
        "password": "teacher456",
        "full_name": "Prof. B. Khan",
        "school_name": "Demo College of Engineering",
    },
]


def is_production_environment() -> bool:
    return (
        os.environ.get("RENDER") == "true"
        or os.environ.get("FLASK_ENV", "").lower() == "production"
        or os.environ.get("APP_ENV", "").lower() == "production"
    )


if __name__ == "__main__":
    allow_demo_seed = os.environ.get("ALLOW_DEMO_SEED", "").lower() in {
        "1",
        "true",
        "yes",
    }
    if is_production_environment() and not allow_demo_seed:
        print(
            "Refusing to seed demo teachers in production. "
            "Set ALLOW_DEMO_SEED=true only if you intentionally want demo accounts."
        )
        raise SystemExit(1)

    with app.app_context():
        db.create_all()
        for row in DEMO_TEACHERS:
            if Teacher.query.filter_by(username=row["username"]).first():
                continue
            t = Teacher(
                username=row["username"],
                full_name=row["full_name"],
                school_name=row["school_name"],
            )
            t.set_password(row["password"])
            db.session.add(t)
        db.session.commit()
        print("Teacher seed complete.")
