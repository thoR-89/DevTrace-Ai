from flask import Flask, render_template, session, redirect
from config import Config
from database.mongodb import check_connection
from routes.auth import auth
from routes.search import search
from routes.history import history

app = Flask(__name__)

app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(search)
app.register_blueprint(history)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session.get("name")
    )


if __name__ == "__main__":

    print("=" * 50)
    print("🚀 DevTrace AI Starting...")
    print("MongoDB Status:", check_connection())
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )