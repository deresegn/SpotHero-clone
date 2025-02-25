from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from models import db, User, ParkingSpot, Booking

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:668866Daw!@localhost:5432/spothero'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Import routes after app initialization
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
