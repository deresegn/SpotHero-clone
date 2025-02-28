from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class ParkingGarage(db.Model):
    __tablename__ = 'parking_garages'  # Match existing table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    amenities = db.Column(db.JSON)  # Store features like "covered", "valet", "security", etc.
    operating_hours = db.Column(db.JSON)  # Store opening hours for each day
    bookings = db.relationship('Booking', backref='parking_garage', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'  # Match existing table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    garage_id = db.Column(db.Integer, db.ForeignKey('parking_garages.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
