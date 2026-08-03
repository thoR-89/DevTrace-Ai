from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from database.mongodb import get_search_history, delete_search_history_item

history = Blueprint("history", __name__)


@history.route("/history")
def history_page():
    """
    Render user-isolated search history dashboard.
    """
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session.get("user")
    history_data = get_search_history(user_email=user_email, limit=50)

    return render_template(
        "history.html",
        history=history_data,
        name=session.get("name")
    )


@history.route("/history/delete/<history_id>", methods=["POST"])
def delete_history(history_id):
    """
    API endpoint to delete a specific search history entry for the logged-in user.
    """
    if "user" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    user_email = session.get("user")
    success = delete_search_history_item(history_id, user_email)

    if success:
        return jsonify({"success": True, "message": "Record deleted successfully"})
    else:
        return jsonify({"success": False, "error": "Record not found or access denied"}), 400