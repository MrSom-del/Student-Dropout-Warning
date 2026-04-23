import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

from extensions import db

API_ENDPOINTS_REQUIRING_AUTH = frozenset(
    {
        "predict.predict",
        "predict.explain",
        "students.get_students",
        "students.get_student",
        "students.high_risk_students",
        "students.analytics",
    }
)


def create_app():

    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(BASE_DIR, "database", "database.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get(
        "FLASK_SECRET_KEY", "dev-change-me-in-production"
    )

    db.init_app(app)

    from models.student_model import Student  # noqa: F401
    from models.teacher_model import Teacher  # noqa: F401

    from routes.predict_routes import predict_bp
    from routes.student_routes import student_bp
    from routes.auth_routes import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(student_bp)

    @app.before_request
    def require_teacher_login():
        if request.endpoint == "static" or request.endpoint is None:
            return
        if request.endpoint in {"auth.login", "auth.guest_login"}:
            return
        if session.get("teacher_id"):
            return
        if request.endpoint in API_ENDPOINTS_REQUIRING_AUTH:
            return jsonify({"error": "Authentication required"}), 401
        return redirect(url_for("auth.login", next=request.path))

    return app


app = create_app()


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)