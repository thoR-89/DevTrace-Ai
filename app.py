import sys
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from database.mongodb import check_connection
from routes.auth import auth
from routes.search import search
from routes.history import history
from routes.dashboard import dashboard_bp

# Ensure stdout handles UTF-8 on Windows consoles safely
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)

# Load Application Configuration
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(search)
app.register_blueprint(history)
app.register_blueprint(dashboard_bp)


@app.route("/")
def home():
    """
    Render modern DevTrace AI landing page.
    """
    return render_template("index.html")


# ---------------------------------------------
# Custom Error Handlers (404, 500)
# ---------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    print("=" * 60)
    print("[+] DevTrace AI Starting Production-Grade Server...")
    db_status = check_connection()
    print(f"[+] MongoDB Connection Status: {'[OK] Connected' if db_status else '[X] Disconnected'}")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )