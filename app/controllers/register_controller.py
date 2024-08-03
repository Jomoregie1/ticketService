from flask import request, jsonify
from app.service.register_service import UserService
from flask import Blueprint

signup = Blueprint("signup", __name__)


@signup.route("/", methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    response, status = UserService.create_user(email, password)

    return jsonify(response), status
