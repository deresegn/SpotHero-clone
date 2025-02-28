from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv
import os
from models import db, User, ParkingGarage, Booking
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:668866Daw!@localhost:5432/ppm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
jwt = JWTManager(app)
db.init_app(app)

# Serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/api/garages', methods=['GET'])
@jwt_required()
def get_garages():
    try:
        garages = ParkingGarage.query.all()
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'address': g.address,
            'total_spots': g.total_spots,
            'price_per_hour': g.price_per_hour,
            'latitude': g.latitude,
            'longitude': g.longitude,
            'description': g.description,
            'amenities': g.amenities,
            'operating_hours': g.operating_hours
        } for g in garages]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    garage = ParkingGarage.query.get_or_404(data['garage_id'])
    
    # Convert string times to datetime
    start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    
    # Calculate duration in hours
    duration = (end_time - start_time).total_seconds() / 3600
    total_price = duration * garage.price_per_hour
    
    # Check if garage has available spots for this time
    concurrent_bookings = Booking.query.filter(
        Booking.garage_id == garage.id,
        Booking.status == 'confirmed',
        db.or_(
            db.and_(Booking.start_time <= start_time, Booking.end_time > start_time),
            db.and_(Booking.start_time < end_time, Booking.end_time >= end_time),
            db.and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
        )
    ).count()
    
    if concurrent_bookings >= garage.total_spots:
        return jsonify({'error': 'No spots available for this time period'}), 400
    
    booking = Booking(
        user_id=current_user_id,
        garage_id=garage.id,
        start_time=start_time,
        end_time=end_time,
        total_price=total_price,
        status='confirmed'
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'id': booking.id,
        'garage': {
            'id': garage.id,
            'name': garage.name,
            'address': garage.address
        },
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
        'total_price': booking.total_price,
        'status': booking.status
    }), 201

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    try:
        current_user_id = get_jwt_identity()
        bookings = Booking.query.filter_by(user_id=current_user_id).all()
        return jsonify([{
            'id': b.id,
            'garage_id': b.garage_id,
            'start_time': b.start_time.isoformat(),
            'end_time': b.end_time.isoformat(),
            'total_price': b.total_price,
            'status': b.status
        } for b in bookings]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)