from flask import render_template
from flask import Blueprint


home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/", methods=['GET'])
def home():
    return render_template("home.html",)
