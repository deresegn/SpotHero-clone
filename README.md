# SpotHero Clone

A full-stack application for finding and booking parking spots, similar to SpotHero.

## Project Structure

```
spothero_clone/
├── backend/           # Flask backend
│   ├── app.py        # Main application file
│   ├── models.py     # Database models
│   └── requirements.txt  # Python dependencies
├── frontend/         # React frontend (to be set up)
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with:
```
DATABASE_URL=sqlite:///spothero.db
JWT_SECRET_KEY=your-secret-key
```

4. Run the backend:
```bash
python app.py
```

### Frontend Setup

1. Install Node.js from: https://nodejs.org/

2. Set up React project:
```bash
cd frontend
npx create-react-app .
```

3. Start the frontend:
```bash
npm start
```

## Features

- User authentication
- Parking spot listing and search
- Booking management
- Real-time availability updates
- Secure payments (to be implemented)

## API Endpoints (To Be Implemented)

- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- GET /api/spots - List parking spots
- POST /api/spots - Create parking spot
- POST /api/bookings - Create booking
- GET /api/bookings - List user bookings
