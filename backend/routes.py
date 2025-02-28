from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import app, db
from models import User, ParkingGarage, Booking
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

@app.route('/api/verify_token', methods=['GET'])
@jwt_required()
def verify_token():
    current_user = get_jwt_identity()
    return jsonify({'valid': True, 'user_id': current_user}), 200

# Parking garage routes
@app.route('/api/garages', methods=['GET'])
@jwt_required()
def get_garages():
    garages = ParkingGarage.query.all()
    return jsonify([{
        'id': garage.id,
        'name': garage.name,
        'address': garage.address,
        'latitude': garage.latitude,
        'longitude': garage.longitude,
        'price_per_hour': garage.price_per_hour,
        'total_spots': garage.total_spots,
        'description': garage.description,
        'amenities': garage.amenities,
        'operating_hours': garage.operating_hours
    } for garage in garages]), 200

@app.route('/api/garages/<int:garage_id>', methods=['GET'])
def get_garage(garage_id):
    garage = ParkingGarage.query.get_or_404(garage_id)
    return jsonify({
        'id': garage.id,
        'name': garage.name,
        'address': garage.address,
        'price_per_hour': garage.price_per_hour,
        'total_spots': garage.total_spots,
        'description': garage.description,
        'amenities': garage.amenities,
        'operating_hours': garage.operating_hours
    }), 200

@app.route('/api/garages', methods=['POST'])
@jwt_required()
def create_garage():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    garage = ParkingGarage(
        owner_id=current_user_id,
        name=data['name'],
        address=data['address'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        price_per_hour=data['price_per_hour'],
        total_spots=data['total_spots'],
        description=data.get('description', ''),
        amenities=data.get('amenities', ''),
        operating_hours=data.get('operating_hours', '')
    )
    
    db.session.add(garage)
    db.session.commit()
    
    return jsonify({
        'id': garage.id,
        'name': garage.name,
        'address': garage.address,
        'latitude': garage.latitude,
        'longitude': garage.longitude,
        'price_per_hour': garage.price_per_hour,
        'total_spots': garage.total_spots,
        'description': garage.description,
        'amenities': garage.amenities,
        'operating_hours': garage.operating_hours
    }), 201

@app.route('/api/garages/<int:garage_id>', methods=['PUT'])
@jwt_required()
def update_garage(garage_id):
    current_user_id = get_jwt_identity()
    garage = ParkingGarage.query.get_or_404(garage_id)
    
    if garage.owner_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403
        
    data = request.get_json()
    garage.name = data.get('name', garage.name)
    garage.price_per_hour = data.get('price_per_hour', garage.price_per_hour)
    garage.total_spots = data.get('total_spots', garage.total_spots)
    garage.description = data.get('description', garage.description)
    garage.amenities = data.get('amenities', garage.amenities)
    garage.operating_hours = data.get('operating_hours', garage.operating_hours)
    
    db.session.commit()
    
    return jsonify({
        'id': garage.id,
        'name': garage.name,
        'price_per_hour': garage.price_per_hour,
        'total_spots': garage.total_spots,
        'description': garage.description,
        'amenities': garage.amenities,
        'operating_hours': garage.operating_hours
    }), 200

@app.route('/api/garages/<int:garage_id>', methods=['DELETE'])
@jwt_required()
def delete_garage(garage_id):
    current_user_id = get_jwt_identity()
    garage = ParkingGarage.query.get_or_404(garage_id)
    
    if garage.owner_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403
        
    db.session.delete(garage)
    db.session.commit()
    
    return jsonify({'message': 'Garage deleted successfully'}), 200

# Booking routes
@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate the garage exists
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
def get_user_bookings():
    current_user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=current_user_id).all()
    return jsonify([{
        'id': booking.id,
        'garage': {
            'id': booking.parking_garage.id,
            'name': booking.parking_garage.name,
            'address': booking.parking_garage.address
        },
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
        'total_price': booking.total_price,
        'status': booking.status
    } for booking in bookings]), 200

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    current_user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user_id:
        return jsonify({'error': 'Not authorized'}), 403
        
    data = request.get_json()
    if 'status' in data:
        booking.status = data['status']
        
        # If booking is cancelled, make the spot available again
        if booking.status == 'cancelled':
            garage = ParkingGarage.query.get(booking.garage_id)
            # garage.available = True
    
    db.session.commit()
    
    return jsonify({
        'id': booking.id,
        'garage_id': booking.garage_id,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
        'total_price': booking.total_price,
        'status': booking.status
    }), 200
