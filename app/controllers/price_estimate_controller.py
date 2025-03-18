from flask import Blueprint, request, render_template
from flask_login import login_required
from app.service.ai_service import AIService
from app.service.item_service import ItemService

estimate_bp = Blueprint("estimate", __name__)

@estimate_bp.route("/", methods=["GET", "POST"])
@login_required
def estimate_page():
    items = ItemService.get_all_items()  # Fetch all items

    estimated_price = None
    error = None

    if request.method == "POST":
        item_id = request.form.get("itemid")
        description = request.form.get("description")

        if not item_id or not description:
            error = "Please select an item and describe the issue."
        else:
            estimated_price = AIService.get_estimate(item_id, description)

    return render_template("estimate.html", items=items, estimated_price=estimated_price, error=error)