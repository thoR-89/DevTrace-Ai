from flask import Blueprint, request, render_template, redirect, session, url_for, flash
from models.user import create_user, verify_user
from utils.helpers import sanitize_input, check_password_strength

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle User Registration with validation and password strength checks.
    """
    if "user" in session:
        return redirect("/dashboard")

    error_msg = None

    if request.method == "POST":
        name = sanitize_input(request.form.get("name", ""))
        email = sanitize_input(request.form.get("email", "")).lower()
        password = request.form.get("password", "")

        # Password strength validation
        strength = check_password_strength(password)
        if strength["score"] < 40:
            error_msg = f"Weak password: {', '.join(strength['feedback'])}"
        else:
            success, msg = create_user(name, email, password)
            if success:
                session["user"] = email
                session["name"] = name
                flash("Account created successfully!", "success")
                return redirect("/dashboard")
            else:
                error_msg = msg

    return render_template(
        "register.html",
        error=error_msg,
        form_name=request.form.get("name", "") if request.method == "POST" else "",
        form_email=request.form.get("email", "") if request.method == "POST" else ""
    )


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle User Authentication & Login Session.
    """
    if "user" in session:
        return redirect("/dashboard")

    error_msg = None

    if request.method == "POST":
        email = sanitize_input(request.form.get("email", "")).lower()
        password = request.form.get("password", "")

        user = verify_user(email, password)
        if user:
            session["user"] = user["email"]
            session["name"] = user["name"]
            session.permanent = True
            return redirect("/dashboard")
        else:
            error_msg = "Invalid email or password. Please try again."

    return render_template("login.html", error=error_msg)


@auth.route("/logout")
def logout():
    """
    Clear session data and redirect to landing page.
    """
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect("/")