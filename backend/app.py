from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models import db, User, ParkingGarage, Booking
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
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

@app.route('/api/verify_token', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 401
            
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email
            }
        }), 200
    except Exception as e:
        app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during token verification'
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Missing email or password'
            }), 400

        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Missing email or password'
            }), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        access_token = create_access_token(identity=user.id)
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email
            }
        }), 200
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login'
        }), 500

@app.route('/api/garages', methods=['GET'])
@jwt_required()
def get_garages():
    try:
        garages = ParkingGarage.query.all()
        return jsonify({
            'success': True,
            'garages': [{
                'id': g.id,
                'name': g.name,
                'address': g.address,
                'total_spots': g.total_spots,
                'price_per_hour': g.price_per_hour,
                'latitude': float(g.latitude),
                'longitude': float(g.longitude),
                'description': g.description,
                'amenities': g.amenities,
                'operating_hours': g.operating_hours
            } for g in garages]
        }), 200
    except Exception as e:
        app.logger.error(f"Garages retrieval error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving garages'
        }), 500

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    try:
        current_user_id = get_jwt_identity()
        bookings = Booking.query.filter_by(user_id=current_user_id).all()
        return jsonify({
            'success': True,
            'bookings': [{
                'id': b.id,
                'garage_id': b.garage_id,
                'start_time': b.start_time.isoformat(),
                'end_time': b.end_time.isoformat(),
                'total_price': float(b.total_price),
                'status': b.status
            } for b in bookings]
        }), 200
    except Exception as e:
        app.logger.error(f"Bookings retrieval error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving bookings'
        }), 500

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        garage_id = data.get('garage_id')
        start_time = datetime.fromisoformat(data.get('start_time'))
        end_time = datetime.fromisoformat(data.get('end_time'))
        
        if not all([garage_id, start_time, end_time]):
            return jsonify({
                'success': False,
                'message': 'Missing required booking information'
            }), 400
            
        garage = ParkingGarage.query.get(garage_id)
        if not garage:
            return jsonify({
                'success': False,
                'message': 'Garage not found'
            }), 404
            
        # Calculate total price
        duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
        total_price = duration * garage.price_per_hour
        
        booking = Booking(
            user_id=current_user_id,
            garage_id=garage_id,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price,
            status='confirmed'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': {
                'id': booking.id,
                'garage_id': booking.garage_id,
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'total_price': float(booking.total_price),
                'status': booking.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Booking creation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while creating booking'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)