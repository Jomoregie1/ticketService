from flask import request, render_template, flash, redirect, url_for
from app.service.user_service import UserService
from app.forms.LoginForm import LoginForm
from flask import Blueprint
from flask_login import login_user
from app.utils import send_password_reset_email

login_bp = Blueprint("login", __name__)


@login_bp.route("/", methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template("login.html", form=form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            user = UserService.check_email_and_password(email, password)

            if user:
                login_user(user)
                flash("Logged in successfully!", "success")

                if user.is_superuser:
                    return redirect(url_for("admin.view_all_tickets"))

                return redirect(url_for("home.home"))
            else:
                flash("Invalid email or password", "danger")

        except Exception as e:
            flash(f"An error occurred during login: {e}", "danger")

    else:
        flash("Please correct the errors in the form.", "danger")

    return render_template("login.html", form=form)


@login_bp.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    """Handles password reset requests."""
    if request.method == "POST":
        email = request.form.get("email")
        user = UserService.get_user_by_email(email)

        if user:
            reset_token = UserService.generate_reset_token(email)
            send_password_reset_email(email, reset_token)
            flash("A password reset link has been sent to your email.", "success")
        else:
            flash("Email not found.", "danger")

    return render_template("forgot_password.html")

@login_bp.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    """Handles the password reset after token verification."""
    email = UserService.verify_reset_token(token)

    if not email:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("login.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
        else:
            UserService.update_password(email, new_password)
            flash("Your password has been reset successfully!", "success")
            return redirect(url_for("login.login"))

    return render_template("reset_password.html", token=token)