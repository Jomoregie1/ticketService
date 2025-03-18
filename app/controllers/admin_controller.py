from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.service.ticket_service import TicketService
from app.service.user_service import UserService
from app.utils import superuser_required
from app.service.item_service import ItemService
from app.utils import superuser_required, send_ticket_completion_email


from flask import render_template
from app.service.ticket_service import TicketService

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/tickets", methods=["GET"])
@login_required
@superuser_required
def view_all_tickets():
    tickets = TicketService.get_all_tickets()  # Fetch all tickets
    items = ItemService.get_all_items()
    sorted_tickets = TicketService.get_tickets_sorted_by_userid()
    return render_template("admin_tickets.html", tickets=tickets, items=items, sorted_tickets=sorted_tickets)  #just added the sorted_tickets


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
    print("🟢 Flask received a request to update ticket!")

    data = request.get_json()
    new_status = data.get("status")

    if new_status is None:
        print("❌ ERROR: No status provided")
        return jsonify({"error": "Missing required field: status"}), 400

    response, status_code = TicketService.update_ticket_status(ticket_id, new_status)

    print(f"🟢 DEBUG: Ticket {ticket_id} updated to {new_status}, Status Code: {status_code}")

    # ✅ Fix the condition to check for "complete" or status = 1
    if status_code == 200 and (str(new_status).lower() == "complete" or str(new_status) == "1"):
        print(f"📩 DEBUG: Fetching ticket details for ticket {ticket_id}...")

        ticket = TicketService.get_ticket_by_id_admin(ticket_id)
        if not ticket:
            print(f"❌ ERROR: Ticket {ticket_id} not found")
            return jsonify({"error": "Ticket not found"}), 404

        print(f"✅ DEBUG: Ticket {ticket_id} found! Fetching user details...")

        user = UserService.get_user_by_id(ticket["userid"])
        if not user:
            print(f"❌ ERROR: User for ticket {ticket_id} not found")
            return jsonify({"error": "User associated with ticket not found"}), 404

        print(f"📩 DEBUG: User {user['email']} found! Sending email...")

        try:
            send_ticket_completion_email(user["email"], ticket_id)
            print(f"✅ EMAIL SENT: Successfully sent email to {user['email']} for ticket {ticket_id}")
        except Exception as e:
            print(f"❌ EMAIL ERROR: Failed to send email - {e}")

    return jsonify(response), status_code

@admin_bp.route("/manufacturer/add", methods=["POST"])
@login_required
@superuser_required
def add_manufacturer():
    data = request.get_json()
    manufacturer_name = data.get("name")

    if not manufacturer_name:
        return jsonify({"error": "Missing required field: name"}), 400

    manufacturer_id, response, status_code = TicketService.add_manufacturer(manufacturer_name)

    if status_code == 201:
        print(f"Manufacturer '{manufacturer_name}' added successfully!")  # Debugging
        return jsonify({"manufacturerid": manufacturer_id, "manufacturername": manufacturer_name}), 201
    else:
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
    print("Manufacturers fetched:", manufacturers)  # Debugging
    return render_template("add_manufacturer.html", manufacturers=manufacturers)

#new stuff

@admin_bp.route("/item/add", methods=["POST"])
@login_required
@superuser_required
def add_item():
    try:
        data = request.get_json()  # Extract JSON data
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        manufacturer_id = data.get("manufacturerid")
        model = data.get("model")
        type_id = data.get("typeid")
        market_price = data.get("market_price")

        if not manufacturer_id or not model or not type_id or not market_price:
            return jsonify({"error": "Missing required fields"}), 400

        # Call service to add item
        item_id, response, status_code = ItemService.add_item(manufacturer_id, model, type_id, market_price)

        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/item/add", methods=["GET"])
@login_required
@superuser_required
def add_item_page():
    manufacturers = TicketService.get_all_manufacturers()  # Fetch manufacturer list
    types = ItemService.get_all_item_types()  # Fetch item types

    return render_template(
        "add_item.html",
        manufacturers=manufacturers,
        types=types
    )