
# Flask and MongoDB Assignment

## Project Description
A Flask web application with a JSON API and a frontend
form that stores submitted data in MongoDB Atlas.

## Features
- GET /api reads records from data/data.json.
- GET / displays the submission form.
- POST /submit validates and saves form data.
- Successful submissions redirect to /success.
- Errors are displayed on the form page.
- Responsive CSS styling.

## Technologies
- Python
- Flask
- MongoDB Atlas
- PyMongo
- HTML and CSS

## Setup Instructions
1. Install Python and Git.
2. Create and activate a virtual environment.
3. Install dependencies using:
   pip install -r requirements.txt
4. Create a .env file and configure MONGO_URI.
5. Run the application:
   python app.py
6. Open http://127.0.0.1:5000/

## API Endpoint
GET http://127.0.0.1:5000/api

## Database
Database: flask_assignment
Collection: submissions

## GitHub Repository
Add your repository URL here after uploading the project.
