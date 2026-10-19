
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for
)
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")

client = None

if MONGO_URI:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )


# Task 1: JSON API route
@app.route("/api")
def api():
    json_file = BASE_DIR / "data" / "data.json"

    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        return jsonify(data)

    except (OSError, json.JSONDecodeError):
        app.logger.exception("Could not read data.json")

        return jsonify({
            "error": "Unable to read the API data file."
        }), 500


# Display the frontend form
@app.route("/")
def home():
    return render_template("index.html")


# Display the success page
@app.route("/success")
def success():
    return render_template("success.html")


# Task 2: Save submitted form data to MongoDB Atlas
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    # Validate form fields
    if not name or not email or not message:
        return render_template(
            "index.html",
            error="Please fill in all fields.",
            name=name,
            email=email,
            message=message
        ), 400

    # Check database configuration
    if client is None:
        return render_template(
            "index.html",
            error="Database is not configured. Please check the .env file.",
            name=name,
            email=email,
            message=message
        ), 500

    try:
        # Verify the database connection
        client.admin.command("ping")

        # Select database and collection
        db = client["flask_assignment"]
        collection = db["submissions"]

        # Insert the form data
        collection.insert_one({
            "name": name,
            "email": email,
            "message": message
        })

        # Redirect only after a successful insert
        return redirect(url_for("success"))

    except PyMongoError:
        app.logger.exception("MongoDB submission failed")

        # Display the error on the same form page
        return render_template(
            "index.html",
            error=(
                "Could not save your data. "
                "Please check the database connection and try again."
            ),
            name=name,
            email=email,
            message=message
        ), 500


if __name__ == "__main__":
    app.run(debug=True)
