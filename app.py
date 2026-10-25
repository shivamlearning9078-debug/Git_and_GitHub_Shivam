
import json
import os
from pathlib import Path
from datetime import datetime, timezone

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

# Initialize Flask application
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


# Task 2: Save regular form data to MongoDB Atlas
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
        # Verify database connection
        client.admin.command("ping")

        # Select database and collection
        db = client["flask_assignment"]
        collection = db["submissions"]

        # Insert regular form data
        collection.insert_one({
            "name": name,
            "email": email,
            "message": message
        })

        # Redirect after successful insertion
        return redirect(url_for("success"))

    except PyMongoError:
        app.logger.exception("MongoDB submission failed")

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


# Task 3: Submit a To-Do item to MongoDB Atlas
@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    item_name = request.form.get("itemName", "").strip()
    item_description = request.form.get(
        "itemDescription", ""
    ).strip()

    # Also accept JSON clients
    if request.is_json:
        data = request.get_json(silent=True) or {}

        item_name = str(data.get("itemName", "")).strip()
        item_description = str(
            data.get("itemDescription", "")
        ).strip()

    # Validate required fields
    if not item_name or not item_description:
        return jsonify({
            "error": "itemName and itemDescription are required"
        }), 400

    # Check database configuration
    if client is None:
        return jsonify({
            "error": "Database is not configured. Please check the .env file."
        }), 500

    # Create To-Do document
    document = {
        "itemName": item_name,
        "itemDescription": item_description,
        "createdAt": datetime.now(timezone.utc)
    }

    try:
        # Verify database connection
        client.admin.command("ping")

        # Use the existing database and collection
        mongo_db = client["flask_assignment"]
        result = mongo_db["submissions"].insert_one(document)

        # JSON clients receive a JSON response
        if request.is_json:
            return jsonify({
                "message": "To-Do item saved successfully",
                "id": str(result.inserted_id)
            }), 201

        # Browser form clients receive a success page
        return render_template(
            "success.html",
            item_name=item_name
        ), 201

    except PyMongoError:
        app.logger.exception("Failed to save To-Do item")

        return jsonify({
            "error": "Unable to save the To-Do item"
        }), 500


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
