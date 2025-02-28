from app import app
from models import db, ParkingGarage
from datetime import datetime

test_garages = [
    {
        'name': 'Downtown Parking Center',
        'address': '123 Main St, San Francisco, CA 94105',
        'latitude': 37.7897,
        'longitude': -122.3987,
        'price_per_hour': 15.00,
        'total_spots': 200,
        'description': 'Centrally located covered parking garage with 24/7 security',
        'amenities': {
            'covered': True,
            'valet': True,
            'security': True,
            'ev_charging': True
        },
        'operating_hours': {
            'monday': {'open': '00:00', 'close': '23:59'},
            'tuesday': {'open': '00:00', 'close': '23:59'},
            'wednesday': {'open': '00:00', 'close': '23:59'},
            'thursday': {'open': '00:00', 'close': '23:59'},
            'friday': {'open': '00:00', 'close': '23:59'},
            'saturday': {'open': '00:00', 'close': '23:59'},
            'sunday': {'open': '00:00', 'close': '23:59'}
        }
    },
    {
        'name': 'Financial District Garage',
        'address': '456 Market St, San Francisco, CA 94105',
        'latitude': 37.7907,
        'longitude': -122.3997,
        'price_per_hour': 20.00,
        'total_spots': 150,
        'description': 'Premium parking in the heart of the Financial District',
        'amenities': {
            'covered': True,
            'valet': True,
            'security': True,
            'car_wash': True
        },
        'operating_hours': {
            'monday': {'open': '06:00', 'close': '22:00'},
            'tuesday': {'open': '06:00', 'close': '22:00'},
            'wednesday': {'open': '06:00', 'close': '22:00'},
            'thursday': {'open': '06:00', 'close': '22:00'},
            'friday': {'open': '06:00', 'close': '22:00'},
            'saturday': {'open': '08:00', 'close': '20:00'},
            'sunday': {'open': '08:00', 'close': '20:00'}
        }
    },
    {
        'name': 'Chinatown Public Parking',
        'address': '789 Grant Ave, San Francisco, CA 94108',
        'latitude': 37.7927,
        'longitude': -122.4067,
        'price_per_hour': 12.00,
        'total_spots': 100,
        'description': 'Affordable parking near Chinatown attractions',
        'amenities': {
            'covered': True,
            'security': True,
            'elevator': True
        },
        'operating_hours': {
            'monday': {'open': '07:00', 'close': '23:00'},
            'tuesday': {'open': '07:00', 'close': '23:00'},
            'wednesday': {'open': '07:00', 'close': '23:00'},
            'thursday': {'open': '07:00', 'close': '23:00'},
            'friday': {'open': '07:00', 'close': '23:00'},
            'saturday': {'open': '07:00', 'close': '23:00'},
            'sunday': {'open': '07:00', 'close': '23:00'}
        }
    }
]

def seed_garages():
    with app.app_context():
        print("Adding test parking garages...")
        for garage_data in test_garages:
            garage = ParkingGarage(**garage_data)
            db.session.add(garage)
        db.session.commit()
        print("Test garages added successfully!")

if __name__ == '__main__':
    seed_garages()
