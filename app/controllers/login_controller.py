from flask import request, jsonify
from app.service.user_service import UserService
from flask import Blueprint
from flask_login import current_user, login_user

login = Blueprint("login", __name__)


@login.route("/", methods=['POST', 'GET'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = check_email_and_password(email, password)

    print(user)

    return jsonify(response), status
