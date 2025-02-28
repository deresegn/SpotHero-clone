from flask import Flask
from models import db, User, ParkingGarage, Booking
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:668866Daw!@localhost:5432/ppm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_test_user():
    # Create a test user
    test_user = User(
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db.session.add(test_user)
    db.session.commit()
    print("Test user created successfully!")

if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
        
        # Check if test user exists
        if not User.query.filter_by(email='test@example.com').first():
            create_test_user()
