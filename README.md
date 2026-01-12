# ScootRapid - Lean E-Scooter Rental Platform

Lightweight and efficient E-Scooter rental platform built with Flask, MySQL, and SQLAlchemy.



## Features

- **User Management**: Simple registration, session-based authentication, role-based access
- **Scooter Management**: Easy scooter tracking with flexible JSON metadata storage
- **Rental System**: Quick rental start/end with automatic cost calculation
- **Payment Processing**: Streamlined payment tracking with multiple methods
- **RESTful API**: Clean API with Marshmallow serialization
- **Web Interface**: Responsive UI with Tailwind CSS

## Technology Stack

- **Backend**: Python 3.9+, Flask 2.3
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Session-based with Flask-Login
- **API**: Flask-RESTful with Marshmallow
- **Frontend**: Jinja2 templates, Tailwind CSS
- **Deployment**: Gunicorn standalone

## Architecture

### Design Patterns
- **Simple MVC**: Direct and efficient data access
- **Active Record Pattern**: Business logic in models
- **Fat Models**: Rich model methods for common operations
- **Functional Utilities**: Helper functions for reusable logic

### Project Structure
```
scoot-rapid/
├── app/
│   ├── models/          # Peewee ORM models
│   ├── controllers/     # Route controllers
│   ├── utils/          # Utilities and helpers
│   ├── templates/      # HTML templates
│   └── static/         # CSS, JS, images
├── api/                # REST API endpoints
├── tests/             # Test suite
├── config.py          # Configuration
├── requirements.txt   # Dependencies
└── wsgi.py           # WSGI entry point
```

## Installation

### Prerequisites
- Python 3.9 or higher
- MySQL 5.7 or higher
- pip and virtualenv

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd scoot-rapid
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Create MySQL database:
```bash
mysql -u root -p
CREATE DATABASE scoot_rapid CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. Initialize database:
```bash
flask init-db
```

7. Create admin user:
```bash
flask create-admin
```

## Running the Application

### Development
```bash
python wsgi.py
```

The application will be available at `http://localhost:5000`

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## API Documentation

### Authentication
Session-based authentication using Flask-Login.

#### Register
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer"
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "message": "Login successful",
  "user": {...}
}
```

### API Endpoints

#### Scooters
- `GET /api/scooters` - List all scooters
- `POST /api/scooters` - Create scooter (Provider/Admin)
- `GET /api/scooters/<id>` - Get scooter details
- `PUT /api/scooters/<id>` - Update scooter
- `DELETE /api/scooters/<id>` - Delete scooter
- `GET /api/scooters/available` - List available scooters
- `GET /api/scooters/nearby?latitude=<lat>&longitude=<lon>` - Find nearby scooters

#### Rentals
- `GET /api/rentals` - List rentals
- `POST /api/rentals` - Start rental
- `GET /api/rentals/<id>` - Get rental details
- `POST /api/rentals/<id>/end` - End rental
- `POST /api/rentals/<id>/cancel` - Cancel rental
- `POST /api/rentals/<id>/rate` - Rate rental

#### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update profile
- `PUT /api/users/me/password` - Change password

## Database Schema

### Users
- Email-based authentication
- Role-based access (admin, provider, customer)
- JSON metadata for flexible data storage

### Scooters
- Unique identifier and QR code
- Location tracking with coordinates
- Battery level monitoring
- Status management
- JSON specs for technical details

### Rentals
- Start/end timestamps and locations
- Duration and cost calculation
- JSON pricing configuration
- Rating and feedback system
- Route distance calculation

### Payments
- Multiple payment methods
- Transaction tracking
- JSON gateway data
- Refund support

## Configuration

### Environment Variables
```bash
# Flask
SECRET_KEY=your-secret-key

# Database
DB_NAME=scoot_rapid
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# Pricing
BASE_PRICE_PER_MINUTE=0.30
START_FEE=1.50

# Limits
MAX_RENTAL_TIME_HOURS=12
```

## Key Differences from ScooterShare Pro

### Simpler Architecture
- Direct model access (Active Record)
- No repository/service layers
- Fat models with business logic
- Utility functions instead of services

### Database
- MySQL instead of PostgreSQL
- Denormalized for read performance
- JSON fields for flexibility
- Simpler schema

### Authentication
- Session-based instead of JWT
- Flask-Login for simplicity
- No token refresh mechanism

### API
- Flask-RESTful instead of Flask-RESTX
- Marshmallow for serialization
- No auto-generated Swagger docs

### Frontend
- Tailwind CSS instead of Bootstrap
- Utility-first styling approach
- Lighter weight

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov=api tests/
```

## Security

- Passwords hashed with bcrypt
- Session-based authentication
- CSRF protection on web forms
- SQL injection prevention via ORM
- Input validation with Marshmallow

## Performance

- Denormalized database for fast reads
- Connection pooling with Peewee
- Efficient queries with Active Record
- JSON fields for flexible data

## Deployment Checklist

- [ ] Set strong SECRET_KEY
- [ ] Configure production database
- [ ] Set DEBUG=False
- [ ] Configure HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure firewall rules

## License

This project is part of an academic assignment for DBWE.TA1A.PA.

## Support

For issues and questions, please contact the development team.
