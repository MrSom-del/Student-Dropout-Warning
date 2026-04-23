import os

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from extensions import db
from models.teacher_model import Teacher

auth_bp = Blueprint("auth", __name__)


def guest_login_enabled() -> bool:
    return os.environ.get("ENABLE_GUEST_LOGIN", "").lower() in {"1", "true", "yes"}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("teacher_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        teacher = Teacher.query.filter_by(username=username).first()
        if teacher and teacher.check_password(password):
            session["teacher_id"] = teacher.id
            session["teacher_name"] = teacher.full_name or teacher.username
            session["school_name"] = teacher.school_name or ""
            next_url = (
                request.form.get("next")
                or request.args.get("next")
                or url_for("index")
            )
            if not next_url.startswith("/") or next_url.startswith("//"):
                next_url = url_for("index")
            return redirect(next_url)

        flash("Invalid username or password.", "danger")

    return render_template("login.html", guest_login_enabled=guest_login_enabled())


@auth_bp.route("/guest-login", methods=["POST"])
def guest_login():
    if not guest_login_enabled():
        flash("Guest access is disabled.", "warning")
        return redirect(url_for("auth.login"))

    session["teacher_id"] = -1
    session["teacher_name"] = "Guest Viewer"
    session["school_name"] = "Demo Access"
    return redirect(url_for("index"))


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("teacher_id", None)
    session.pop("teacher_name", None)
    session.pop("school_name", None)
    return redirect(url_for("auth.login"))
