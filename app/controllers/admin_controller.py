from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.service.ticket_service import TicketService
from app.service.user_service import UserService
from app.utils import superuser_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/tickets", methods=["GET"])
@login_required
@superuser_required
def view_all_tickets():
    tickets = TicketService.get_all_tickets()  # Fetch all tickets
    return render_template("admin_tickets.html", tickets=tickets)


@admin_bp.route("/user/delete/<int:user_id>", methods=["POST"])
@login_required
@superuser_required
def delete_user(user_id):
    response, status_code = UserService.delete_user(user_id)
    return jsonify(response), status_code


@admin_bp.route("/user/update/<int:user_id>", methods=["POST"])
@login_required
@superuser_required
def update_user(user_id):
    data = request.get_json()
    response, status_code = UserService.update_user(user_id, data)
    return jsonify(response), status_code


@admin_bp.route("/ticket/delete/<int:ticket_id>", methods=["POST"])
@login_required
@superuser_required
def delete_ticket(ticket_id):
    response, status_code = TicketService.delete_ticket_superuser(ticket_id, is_superuser=True)
    return jsonify(response), status_code


@admin_bp.route("/ticket/update/status/<int:ticket_id>", methods=["POST"])
@login_required
@superuser_required
def update_ticket_status(ticket_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status is None:
        return jsonify({"error": "Missing required field: status"}), 400

    response, status_code = TicketService.update_ticket_status(ticket_id, new_status)
    return jsonify(response), status_code


@admin_bp.route("/manufacturer/add", methods=["POST"])
@login_required
@superuser_required
def add_manufacturer():
    data = request.get_json()
    manufacturer_name = data.get("name")

    if not manufacturer_name:
        return jsonify({"error": "Missing required field: name"}), 400

    response, status_code = TicketService.add_manufacturer(manufacturer_name)
    return jsonify(response), status_code


@admin_bp.route("/users", methods=["GET"])
@login_required
@superuser_required
def view_all_users():
    users = UserService.get_all_users()
    return render_template("admin_users.html", users=users)


@admin_bp.route("/manufacturer/add", methods=["GET"])
@login_required
@superuser_required
def add_manufacturer_page():
    manufacturers = TicketService.get_all_manufacturers()
    return render_template("add_manufacturer.html", manufacturers=manufacturers)
