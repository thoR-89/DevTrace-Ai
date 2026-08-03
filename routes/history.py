from flask import Blueprint, render_template, session, redirect
from database.mongodb import get_search_history

history = Blueprint("history", __name__)


@history.route("/history")
def history_page():

    if "user" not in session:
        return redirect("/login")

    history_data = get_search_history()

    return render_template(
        "history.html",
        history=history_data
    )