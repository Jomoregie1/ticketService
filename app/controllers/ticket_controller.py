from datetime import datetime

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app.forms.TicketForm import TicketForm  #uses the ticket form for creation and updates
from app.service.ticket_service import TicketService #database operations
from app.service.item_service import ItemService #used to make simple for the user by using the drop down menus

ticket_bp = Blueprint("ticket", __name__)


@ticket_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket_page():
    form = TicketForm() #ues form

    # Fetch items dynamically for dropdown menu to allow the user to easily select a item
    try:
        items = ItemService.get_all_items()
        form.itemid.choices = [(item["id"], item["name"]) for item in items]
    except Exception as e:
        flash(f"Error fetching items: {e}", "danger")
        form.itemid.choices = []

    if form.validate_on_submit():     #sets the data by the form
        description = form.description.data
        status = False  #open
        itemid = form.itemid.data
        userid = current_user.id

        # Call TicketService to create ticket  using the data submitted
        response, status_code = TicketService.create_ticket(description, status, userid, itemid)

        if status_code == 201: #debug
            flash(f"Ticket created successfully! Detected Issues: {response['detected_issues']}", "success")
            return redirect(url_for("ticket.ticket_page"))
        else:
            flash(response.get("error", "Failed to create ticket. Try again."), "danger")
            return redirect(url_for("ticket.create_ticket_page"))

    return render_template("createTicket.html", form=form)

@ticket_bp.route("/delete/<int:ticket_id>", methods=["POST"])
@login_required
def delete_ticket(ticket_id):
    userid = current_user.id
    response, status_code = TicketService.delete_ticket(ticket_id, userid) #calls function to delete ticket

    return jsonify(response), status_code


@ticket_bp.route("/update/<int:ticket_id>", methods=["POST"])
@login_required
def update_ticket(ticket_id):

    if not current_user.is_authenticated:       #checks if user is logged with correct account
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    userid = current_user.id

    ticket = TicketService.get_ticket_by_id(ticket_id, userid) #fetches ticket

    if not ticket:
        return jsonify({"error": "Ticket not found or unauthorized"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400
#extracts the new values
    description = data.get("description")
    itemid = data.get("itemid")

    if not description or not itemid:
        return jsonify({"error": "Missing required fields"}), 400

    response, status_code = TicketService.update_ticket(ticket_id, userid, description, itemid)  #sends data to be inserted into DB

    print("Update Response:", response, "Status Code:", status_code)
    return jsonify(response), status_code


@ticket_bp.route("/", methods=["GET"])
@login_required
def ticket_page():

    #Render a page listing all tickets for the current user.
    #admins can see all tickets (super user)

    userid = current_user.id
    if current_user.is_superuser:
        tickets = TicketService.get_all_tickets()
    else:
        tickets = TicketService.get_tickets_by_user(userid)

    try:
        items = ItemService.get_all_items()
        if items is None:
            items = []
    except Exception as e:
        items = []

    return render_template("viewTicket.html", tickets=tickets, items=items)