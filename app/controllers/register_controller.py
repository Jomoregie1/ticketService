from flask import request, flash, redirect, url_for, render_template
from flask import Blueprint
from flask_login import current_user, login_user
from app.forms.RegisterForm import RegisterForm
from app.models.userModel import User
from app import db

signup = Blueprint("signup", __name__)


@signup.route("/", methods=['POST', 'GET'])
def register():

    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("home.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("You registered and are now logged in. Welcome!", "success")

        return redirect(url_for("login.login"))

    return render_template("register.html", form=form)
