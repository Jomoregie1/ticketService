from flask import request, flash, redirect, url_for, render_template
from flask import Blueprint
from flask_login import current_user, login_user
from app.forms.RegisterForm import RegisterForm
from app.service.user_service import UserService

signup = Blueprint("signup", __name__)


@signup.route("/", methods=['POST', 'GET'])
def register():
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("home.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Use UserService to create the user
        response, status_code = UserService.create_user(form.email.data, form.password.data)

        if status_code == 201:  # Successful registration
            flash(response["message"], "success")

            # Log the user in
            user = UserService.check_email_and_password(form.email.data, form.password.data)
            if user:
                login_user(user)

            return redirect(url_for("login.login"))
        else:
            # Handle errors (e.g., email already in use)
            flash(response["error"], "danger")

    return render_template("register.html", form=form)
