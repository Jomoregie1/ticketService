from functools import wraps
from flask import jsonify, redirect, url_for
from flask_login import current_user
from flask_mail import Message   #email stuff dont move or restart flask
from app import mail
from app.service.item_service import ItemService
from app.service.ticket_service import TicketService
from flask import url_for

def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_superuser", False):
            return jsonify(
                {"error": "Unauthorized. Superuser access required."}), 403

        return f(*args, **kwargs)

    return decorated_function


#new email thing
def send_ticket_completion_email(user_email, ticket_id):
    #  ticket details
    ticket = TicketService.get_ticket_by_id_admin(ticket_id)

    if not ticket:
        print(f" ERROR: Ticket {ticket_id} not found, cannot send email.")
        return

    # item details
    item = ItemService.get_item_by_id(ticket["itemid"])

    item_name = item["name"] if item else "Unknown Item"


    subject = "Your Ticket Has Been Resolved"
    body = (
        f"Hello,\n\n"
        f"Your ticket (ID: {ticket_id}) for **{item_name}** has been marked as complete.\n\n"
        f"Thank you for using our service!\n\n"
        f"Best regards,\nSupport Team"
    )

    msg = Message(subject, recipients=[user_email], body=body)

    try:
        mail.send(msg)
        print(f" EMAIL SENT: Successfully sent email to {user_email} for ticket {ticket_id} ({item_name})")
    except Exception as e:
        print(f"EMAIL ERROR: Failed to send email - {e}")


def send_password_reset_email(user_email, reset_token):

    reset_url = url_for("login.reset_password", token=reset_token, _external=True)

    subject = "Password Reset Request"
    body = (
        f"Hello,\n\n"
        f"You requested a password reset. Click the link below to reset your password:\n\n"
        f"{reset_url}\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\nSupport Team"
    )

    msg = Message(subject, recipients=[user_email], body=body)

    try:
        mail.send(msg)
        print(f" PASSWORD RESET EMAIL SENT to {user_email}")
    except Exception as e:
        print(f" EMAIL ERROR: Failed to send password reset email - {e}")
