"""Create one teacher account manually.

Usage:
  python create_teacher.py --username myuser --password 'StrongPass123!' --name 'My Name' --school 'My School'
"""

import argparse

from app import app
from extensions import db
from models.teacher_model import Teacher


def parse_args():
    parser = argparse.ArgumentParser(description="Create a teacher account.")
    parser.add_argument("--username", required=True, help="Teacher username")
    parser.add_argument("--password", required=True, help="Teacher password")
    parser.add_argument("--name", default="", help="Full name")
    parser.add_argument("--school", default="", help="School name")
    return parser.parse_args()


def validate_inputs(username: str, password: str):
    username = (username or "").strip()
    if not username:
        raise ValueError("Username is required.")
    if len(password or "") < 8:
        raise ValueError("Password must be at least 8 characters.")
    return username


if __name__ == "__main__":
    args = parse_args()
    username = validate_inputs(args.username, args.password)

    with app.app_context():
        db.create_all()
        existing = Teacher.query.filter_by(username=username).first()
        if existing:
            print(f"Teacher '{username}' already exists. No change made.")
            raise SystemExit(0)

        teacher = Teacher(
            username=username,
            full_name=(args.name or "").strip() or None,
            school_name=(args.school or "").strip() or None,
        )
        teacher.set_password(args.password)
        db.session.add(teacher)
        db.session.commit()

    print(f"Created teacher account: {username}")
