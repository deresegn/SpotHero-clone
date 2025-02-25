from app import app, db
from models import User, ParkingSpot, Booking
from datetime import datetime, timedelta, timezone

def add_test_data():
    try:
        app.app_context().push()
        
        # Get our test user
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            print("Test user not found!")
            return

        # Create some test parking spots
        spots = [
            ParkingSpot(
                owner_id=user.id,
                address="123 Main St, San Francisco, CA",
                price_per_hour=15.0,
                description="Convenient downtown parking spot near shopping center",
                available=True
            ),
            ParkingSpot(
                owner_id=user.id,
                address="456 Market St, San Francisco, CA",
                price_per_hour=20.0,
                description="Secure garage parking in financial district",
                available=True
            ),
            ParkingSpot(
                owner_id=user.id,
                address="789 Mission St, San Francisco, CA",
                price_per_hour=12.0,
                description="Open parking lot near SOMA",
                available=True
            )
        ]

        # Add spots to database
        for spot in spots:
            db.session.add(spot)
        db.session.commit()

        # Create some test bookings
        now = datetime.now(timezone.utc)  # Use timezone-aware datetime
        bookings = [
            Booking(
                user_id=user.id,
                spot_id=spots[0].id,
                start_time=now + timedelta(days=1),
                end_time=now + timedelta(days=1, hours=2),
                total_price=30.0,
                status='confirmed'
            ),
            Booking(
                user_id=user.id,
                spot_id=spots[1].id,
                start_time=now + timedelta(days=2),
                end_time=now + timedelta(days=2, hours=3),
                total_price=60.0,
                status='pending'
            )
        ]

        # Add bookings to database
        for booking in bookings:
            db.session.add(booking)
        db.session.commit()

        print("Successfully added test parking spots and bookings!")
        
        # Print the data we just added
        print("\nParking Spots:")
        for spot in ParkingSpot.query.all():
            print(f"ID: {spot.id}, Address: {spot.address}, Price: ${spot.price_per_hour}/hour")
        
        print("\nBookings:")
        for booking in Booking.query.all():
            print(f"ID: {booking.id}, Spot ID: {booking.spot_id}, Status: {booking.status}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        db.session.rollback()
    finally:
        try:
            app.app_context().pop()
        except:
            pass

if __name__ == '__main__':
    add_test_data()
