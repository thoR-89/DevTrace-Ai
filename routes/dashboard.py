from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from database.mongodb import get_search_history, get_analytics_stats

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/dashboard", endpoint="dashboard")
def dashboard():
    """
    Render main developer search dashboard with recent searches and metrics.
    """
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session.get("user")
    recent_history = get_search_history(user_email=user_email, limit=5)
    stats = get_analytics_stats()

    return render_template(
        "dashboard.html",
        name=session.get("name"),
        recent_history=recent_history,
        stats=stats
    )


@dashboard_bp.route("/api/admin/stats")
def admin_stats():
    """
    JSON API endpoint returning aggregated system analytics for Chart.js dashboard charts.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    stats = get_analytics_stats()
    return jsonify(stats)
