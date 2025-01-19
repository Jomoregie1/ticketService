from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app.forms.TicketForm import TicketForm
from app.service.ticket_service import TicketService
from app.service.item_service import ItemService

ticket_bp = Blueprint("ticket", __name__)


@ticket_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket_page():

    form = TicketForm()  # Instantiate the form

    # Fetch items dynamically for the dropdown
    try:
        items = ItemService.get_all_items()
        form.itemid.choices = [(item["id"], item["name"]) for item in items]
    except Exception as e:
        flash(f"Error fetching items: {e}", "danger")
        form.itemid.choices = []  # Empty dropdown in case of error

    if form.validate_on_submit():  # Handles POST request
        description = form.description.data
        status = form.status.data
        itemid = form.itemid.data
        userid = current_user.id

        print(description, status,itemid, userid)

        # Call the TicketService to create the ticket
        response, status_code = TicketService.create_ticket(description, status, userid, itemid)
        print(response)

        if status_code == 201:
            flash("Ticket created successfully!", "success")
            return redirect(url_for("ticket.ticket_page"))
        else:
            flash(response.get("error", "Failed to create ticket. Try again."), "danger")
            return redirect(url_for("ticket.create_ticket_page"))

    # Render the form for GET request or after failed validation
    return render_template("ticket.html", form=form)


@ticket_bp.route("/", methods=["GET"])
@login_required
def ticket_page():
    """
    Render a page listing all tickets for the current user.
    """
    userid = current_user.id
    tickets = TicketService.get_tickets_by_user(userid)  # Fetch tickets for the logged-in user
    return render_template("ticket.html", tickets=tickets)
