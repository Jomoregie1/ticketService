from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.service.user_service import UserService
from app.utils import superuser_required
from app.service.item_service import ItemService
from app.utils import superuser_required, send_ticket_completion_email   #email functionality
from flask import render_template
from app.service.ticket_service import TicketService

#defines the admin blueprint
admin_bp = Blueprint("admin", __name__)

#ticket page. main hub


@admin_bp.route("/tickets", methods=["GET"])
@login_required
@superuser_required
def view_all_tickets():
    #this is a page that displays all the tickets in the system. it is sorted so that the html can use binary search
    #as the search method
    tickets = TicketService.get_all_tickets()  # fetches all tickets
    items = ItemService.get_all_items()
    sorted_tickets = TicketService.get_tickets_sorted_by_userid()
    return render_template("admin_tickets.html", tickets=tickets, items=items, sorted_tickets=sorted_tickets)  #just added the sorted_tickets



#user management


@admin_bp.route("/user/delete/<int:user_id>", methods=["POST"])
@login_required
@superuser_required
def delete_user(user_id):
    #this is a route to delete a user using their ID
    response, status_code = UserService.delete_user(user_id)
    return jsonify(response), status_code


@admin_bp.route("/user/update/<int:user_id>", methods=["POST"])
@login_required
@superuser_required
def update_user(user_id):
    #this is a route that is used to update a users status. can be used for other details if allowed
    data = request.get_json()
    response, status_code = UserService.update_user(user_id, data)
    return jsonify(response), status_code

@admin_bp.route("/users", methods=["GET"])
@login_required
@superuser_required
def view_all_users():
    #page to veiw all users who are not of admin status
    users = UserService.get_all_users()
    return render_template("admin_users.html", users=users)



#ticket management


@admin_bp.route("/ticket/delete/<int:ticket_id>", methods=["POST"])
@login_required
@superuser_required
def delete_ticket(ticket_id):
    #allows the admin to delete any ticket in the system due to being a superuser
    response, status_code = TicketService.delete_ticket_superuser(ticket_id, is_superuser=True)
    return jsonify(response), status_code


@admin_bp.route("/ticket/update/status/<int:ticket_id>", methods=["POST"])
@login_required
@superuser_required
def update_ticket_status(ticket_id):
    #allows an admin to update tiket status. this also calls utils.py to send an email to the user
    #alot of debugging as issues did arrise but have been fixed. AI assistance was used for debugging and some writing
    #everything related to the Email has used AI assistance
    print("Flask received a request to update ticket")

    data = request.get_json()
    new_status = data.get("status")

    if new_status is None:
        print("No status provided")
        return jsonify({"error": "Missing required field: status"}), 400

    response, status_code = TicketService.update_ticket_status(ticket_id, new_status)

    print(f" Ticket {ticket_id} updated to {new_status}, Status Code: {status_code}")

    # Fix the condition to check for "complete" or status = 1
    if status_code == 200 and (str(new_status).lower() == "complete" or str(new_status) == "1"):
        print(f" Fetching ticket details for ticket {ticket_id}...")

        ticket = TicketService.get_ticket_by_id_admin(ticket_id)
        if not ticket:
            print(f" ERROR: Ticket {ticket_id} not found")
            return jsonify({"error": "Ticket not found"}), 404



        user = UserService.get_user_by_id(ticket["userid"])
        if not user:
            print(f"ERROR: User for ticket {ticket_id} not found")
            return jsonify({"error": "User associated with ticket not found"}), 404



        try:
            send_ticket_completion_email(user["email"], ticket_id)
            print(f"EMAIL SENT: Successfully sent email to {user['email']} for ticket {ticket_id}")
        except Exception as e:
            print(f"EMAIL ERROR: Failed to send email - {e}")

    return jsonify(response), status_code


#Manufactuer management


@admin_bp.route("/manufacturer/add", methods=["POST"])
@login_required
@superuser_required
def add_manufacturer():
    #here is an admin route to add a new manufactuerer to the system
    data = request.get_json()
    manufacturer_name = data.get("name")

    if not manufacturer_name:
        return jsonify({"error": "Missing required field: name"}), 400

    manufacturer_id, response, status_code = TicketService.add_manufacturer(manufacturer_name)   #calls ticket service to perform insertion of data to sql

    if status_code == 201:
        print(f"Manufacturer '{manufacturer_name}' added successfully!")  # Debugging to ensure it has been added to DB
        return jsonify({"manufacturerid": manufacturer_id, "manufacturername": manufacturer_name}), 201
    else:
        return jsonify(response), status_code




@admin_bp.route("/manufacturer/add", methods=["GET"])
@login_required
@superuser_required
def add_manufacturer_page():
    #here is the page to add an admin
    manufacturers = TicketService.get_all_manufacturers()
    print("Manufacturers fetched:", manufacturers)  # Debugging
    return render_template("add_manufacturer.html", manufacturers=manufacturers)

#add an item/ item management

@admin_bp.route("/item/add", methods=["POST"])
@login_required
@superuser_required
def add_item():

    #admin route to add a new item/ device.
    try:
        data = request.get_json()  # Extract JSON data
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        manufacturer_id = data.get("manufacturerid")
        model = data.get("model")
        type_id = data.get("typeid")
        market_price = data.get("market_price")

        if not manufacturer_id or not model or not type_id or not market_price: #makes sure all values have data
            return jsonify({"error": "Missing required fields"}), 400

        # ueses item service to insert it into DB
        item_id, response, status_code = ItemService.add_item(manufacturer_id, model, type_id, market_price)

        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/item/add", methods=["GET"])
@login_required
@superuser_required
def add_item_page():
    #here is a page for the items. it gets the manufactuers and types to display in a simple drop down menu for extra ease
    #a form is renderd for adding new items/devices
    manufacturers = TicketService.get_all_manufacturers()
    types = ItemService.get_all_item_types()

    return render_template(
        "add_item.html",
        manufacturers=manufacturers,
        types=types
    )