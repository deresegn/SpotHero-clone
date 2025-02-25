from flask import current_app
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def test_create_user():
    try:
        app.app_context().push()  # Properly set up the application context
        print("Creating test user...")
        # Create a test user
        test_user = User(
            email='test@example.com',
            password=generate_password_hash('password123')
        )
        
        # Add to database
        print("Adding user to database...")
        db.session.add(test_user)
        db.session.commit()
        
        # Query to verify
        print("Verifying user was created...")
        user = User.query.filter_by(email='test@example.com').first()
        if user:
            print(f"Created user with ID: {user.id} and email: {user.email}")
        else:
            print("Failed to find user after creation")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
    finally:
        try:
            app.app_context().pop()  # Clean up the context
        except:
            pass

if __name__ == '__main__':
    test_create_user()
