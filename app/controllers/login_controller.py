from flask import request, jsonify,render_template,flash,redirect,url_for
from app.service.user_service import UserService
from flask import Blueprint
from flask_login import current_user, login_user

login_bp = Blueprint("login", __name__)


@login_bp.route("/", methods=['POST', 'GET'])
def login():

    if request.method == 'GET':
        return render_template("login.html")

    if request.content_type == "application/json":
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

    if not email or not password:

        if request.content_type == "application/json":
            return jsonify({"error": "Email and password are required"}), 400
        else:
            flash("Email and password are required", "danger")
            return render_template("login.html")

    user = UserService.check_email_and_password(email, password)

    if user:
        login_user(user)
        flash("logged in sucessfully!", "success")
        return redirect(url_for("home.home"))
    else:
        flash("Invalid email or password", "danger")
        return render_template("login.html")
