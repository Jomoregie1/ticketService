from flask import request, flash, redirect, url_for, render_template
from flask import Blueprint
from flask_login import current_user, login_user
from app.forms.RegisterForm import RegisterForm
from app.service.user_service import UserService

signup = Blueprint("signup", __name__)


@signup.route("/", methods=['POST', 'GET'])
def register():

    if current_user.is_authenticated:           #already in DB
        flash("You are already registered.", "info")
        redirect(url_for("signup.register"))


    form = RegisterForm()
    if form.validate_on_submit():

        response, status_code = UserService.create_user(form.email.data, form.password.data)

        if status_code == 201:  #it did the registration
            flash(response["message"], "success")


            user = UserService.check_email_and_password(form.email.data, form.password.data)
            if user:
                login_user(user)

            return redirect(url_for("login.login"))
        else:
            # error or exception handling
            flash(response["error"], "danger")

    return render_template("register.html", form=form)
