from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import app, db
from models import User, ParkingSpot, Booking
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
        
    user = User(
        email=data['email'],
        password=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200

# Parking spot routes
@app.route('/api/spots', methods=['GET'])
def get_spots():
    spots = ParkingSpot.query.filter_by(available=True).all()
    return jsonify([{
        'id': spot.id,
        'address': spot.address,
        'price_per_hour': spot.price_per_hour,
        'description': spot.description
    } for spot in spots]), 200

@app.route('/api/spots/<int:spot_id>', methods=['GET'])
def get_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    return jsonify({
        'id': spot.id,
        'address': spot.address,
        'price_per_hour': spot.price_per_hour,
        'description': spot.description,
        'available': spot.available
    }), 200

@app.route('/api/spots', methods=['POST'])
@jwt_required()
def create_spot():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    spot = ParkingSpot(
        owner_id=current_user_id,
        address=data['address'],
        price_per_hour=data['price_per_hour'],
        description=data.get('description', '')
    )
    
    db.session.add(spot)
    db.session.commit()
    
    return jsonify({
        'id': spot.id,
        'address': spot.address,
        'price_per_hour': spot.price_per_hour,
        'description': spot.description
    }), 201

@app.route('/api/spots/<int:spot_id>', methods=['PUT'])
@jwt_required()
def update_spot(spot_id):
    current_user_id = int(get_jwt_identity())
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    if spot.owner_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403
        
    data = request.get_json()
    spot.address = data.get('address', spot.address)
    spot.price_per_hour = data.get('price_per_hour', spot.price_per_hour)
    spot.description = data.get('description', spot.description)
    spot.available = data.get('available', spot.available)
    
    db.session.commit()
    
    return jsonify({
        'id': spot.id,
        'address': spot.address,
        'price_per_hour': spot.price_per_hour,
        'description': spot.description,
        'available': spot.available
    }), 200

@app.route('/api/spots/<int:spot_id>', methods=['DELETE'])
@jwt_required()
def delete_spot(spot_id):
    current_user_id = int(get_jwt_identity())
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    if spot.owner_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403
        
    db.session.delete(spot)
    db.session.commit()
    
    return jsonify({'message': 'Spot deleted successfully'}), 200

# Booking routes
@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Convert string datetime to Python datetime
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time'])
    
    spot = ParkingSpot.query.get_or_404(data['spot_id'])
    if not spot.available:
        return jsonify({'error': 'Spot is not available'}), 400
        
    booking = Booking(
        user_id=current_user_id,
        spot_id=data['spot_id'],
        start_time=start_time,
        end_time=end_time,
        total_price=spot.price_per_hour * float(data['hours'])
    )
    
    spot.available = False
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'id': booking.id,
        'spot_id': booking.spot_id,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
        'total_price': booking.total_price,
        'status': booking.status
    }), 201

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    current_user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([{
        'id': booking.id,
        'spot_id': booking.spot_id,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
        'total_price': booking.total_price,
        'status': booking.status
    } for booking in bookings]), 200

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    current_user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403
        
    data = request.get_json()
    if 'status' in data:
        booking.status = data['status']
        
        # If booking is cancelled, make the spot available again
        if booking.status == 'cancelled':
            spot = ParkingSpot.query.get(booking.spot_id)
            spot.available = True
    
    db.session.commit()
    
    return jsonify({
        'id': booking.id,
        'spot_id': booking.spot_id,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
        'total_price': booking.total_price,
        'status': booking.status
    }), 200
