from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app.forms.TicketForm import TicketForm
from app.service.ticket_service import TicketService
from app.service.item_service import ItemService

ticket_bp = Blueprint("ticket", __name__)


@ticket_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket_page():
    """
    Render and handle the ticket creation form.
    """
    form = TicketForm()  # Instantiate the form

    if request.method == "POST":
        # Get form data
        description = form.description.data
        status = form.status.data
        itemid = form.itemid.data

        # Validate required fields
        if not form.validate_on_submit():
            flash("All fields are required!", "danger")
            return redirect(url_for("ticket.create_ticket_page"))

        userid = current_user.id

        # Call the TicketService to create the ticket
        response, status_code = TicketService.create_ticket(description, status, userid, itemid)

        if status_code == 201:
            flash("Ticket created successfully!", "success")
            return redirect(url_for("ticket.ticket_page"))  # Redirect to the ticket page
        else:
            flash(response.get("error", "Failed to create ticket. Try again."), "danger")
            return redirect(url_for("ticket.create_ticket_page"))

    # Fetch items dynamically for the dropdown
    try:
        items = ItemService.get_all_items()
        print(items)  # Log the output to verify
        form.itemid.choices = [(item["id"], item["name"]) for item in items]
    except Exception as e:
        flash(f"Error fetching items: {e}", "danger")
        form.itemid.choices = []  # Empty dropdown in case of error

    return render_template("ticket.html", form=form, items=items)


@ticket_bp.route("/", methods=["GET"])
@login_required
def ticket_page():
    """
    Render a page listing all tickets for the current user.
    """
    userid = current_user.id
    tickets = TicketService.get_tickets_by_user(userid)  # Fetch tickets for the logged-in user
    return render_template("tickets.html", tickets=tickets)
