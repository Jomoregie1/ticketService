from flask import request, jsonify, render_template
from app.service.user_service import UserService
from flask import Blueprint
from flask_login import current_user, login_user

home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/", methods=['GET'])
def home():
    return render_template("home.html")
