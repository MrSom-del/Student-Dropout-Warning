from extensions import db
from datetime import datetime

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    code_module = db.Column(db.Integer)
    code_presentation = db.Column(db.Integer)
    gender = db.Column(db.Integer)
    region = db.Column(db.Integer)
    highest_education = db.Column(db.Integer)
    imd_band = db.Column(db.Integer)
    age_band = db.Column(db.Integer)
    num_of_prev_attempts = db.Column(db.Integer)
    studied_credits = db.Column(db.Integer)
    disability = db.Column(db.Integer)

    total_clicks = db.Column(db.Integer)
    active_days = db.Column(db.Integer)
    unique_resources = db.Column(db.Integer)
    num_forum = db.Column(db.Integer)
    num_quiz = db.Column(db.Integer)
    avg_score = db.Column(db.Float)
    num_assess_attempted = db.Column(db.Integer)
    total_weight = db.Column(db.Integer)
    module_presentation_length = db.Column(db.Integer)

    dropout_probability = db.Column(db.Float)
    risk_level = db.Column(db.String(10))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)