from flask import request, jsonify, render_template, flash, redirect, url_for
from app.service.user_service import UserService
from app.forms.LoginForm import LoginForm
from flask import Blueprint
from flask_login import current_user, login_user

login_bp = Blueprint("login", __name__)


@login_bp.route("/", methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template("login.html", form=form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = UserService.check_email_and_password(email, password)

        if user:
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home.home"))
        else:
            flash("Invalid email or password", "danger")

    else:
        flash("Please correct the errors in the form.", "danger")

    return render_template("login.html", form=form)
