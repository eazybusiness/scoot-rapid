# ScootRapid API Test Commands

## 🚀 API Testing Guide

This document contains all the curl commands to test the ScootRapid API after deployment.

### Base URL
```
https://scoot-rapid-production.up.railway.app
```

## 📋 Test Commands

### 1. Health Check
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/health \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-10T11:09:23.123456",
  "version": "1.0.0"
}
```

### 2. User Login
```bash
curl -X POST https://scoot-rapid-production.up.railway.app/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "customer"
  }
}
```

### 3. Get All Scooters (Requires Auth)
```bash
# Replace YOUR_TOKEN with the access token from login
curl -X GET https://scoot-rapid-production.up.railway.app/api/scooters \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "scooters": [
    {
      "id": 1,
      "model": "Xiaomi Mi Electric Scooter Pro 2",
      "license_plate": "SC-001-AB",
      "location": "Hauptbahnhof Zürich",
      "battery_level": 85,
      "status": "available",
      "created_at": "2026-01-10T10:00:00"
    }
  ]
}
```

### 4. Get Available Scooters (Requires Auth)
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/scooters/available \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Specific Scooter (Requires Auth)
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/scooters/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Get User Rentals (Requires Auth)
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/rentals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Get User Statistics (Requires Auth)
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/stats \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Start Rental (Requires Auth)
```bash
curl -X POST https://scoot-rapid-production.up.railway.app/api/rentals/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "scooter_id": 1
  }'
```

**Expected Response:**
```json
{
  "message": "Rental started successfully",
  "rental": {
    "id": 1,
    "scooter": {
      "id": 1,
      "model": "Xiaomi Mi Electric Scooter Pro 2",
      "license_plate": "SC-001-AB"
    },
    "start_time": "2026-01-10T11:09:23.123456",
    "status": "active"
  }
}
```

### 9. End Rental (Requires Auth)
```bash
curl -X POST https://scoot-rapid-production.up.railway.app/api/rentals/1/end \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "message": "Rental ended successfully",
  "rental": {
    "id": 1,
    "end_time": "2026-01-10T11:15:23.123456",
    "total_cost": 2.70,
    "duration_formatted": "6 Minuten",
    "status": "completed"
  }
}
```

## 🔧 Error Testing

### Invalid Login
```bash
curl -X POST https://scoot-rapid-production.up.railway.app/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid@example.com",
    "password": "wrongpassword"
  }'
```

**Expected Response:**
```json
{
  "error": "Invalid credentials"
}
```
**Status Code:** 401

### Unauthorized Access
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/scooters \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "error": "Missing Authorization Header"
}
```
**Status Code:** 401

### Invalid Endpoint
```bash
curl -X GET https://scoot-rapid-production.up.railway.app/api/invalid \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "error": "Not found"
}
```
**Status Code:** 404

## 📱 Mobile App Integration

For mobile app development, use these endpoints:

### Authentication Flow
1. **Login:** `POST /api/login` - Get JWT token
2. **Include token** in all subsequent requests: `Authorization: Bearer TOKEN`

### Core Features
1. **Browse Scooters:** `GET /api/scooters/available`
2. **Start Rental:** `POST /api/rentals/start`
3. **End Rental:** `POST /api/rentals/{id}/end`
4. **View History:** `GET /api/rentals`
5. **User Stats:** `GET /api/stats`

### Response Format
All responses are in JSON format with appropriate HTTP status codes:
- `200` - Success
- `201` - Created (for new resources)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## 🧪 Automated Testing

Run the automated test suite:
```bash
python3 test_api.py
```

This will test all endpoints and generate a detailed report.

## 📊 API Documentation

### Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/login` | No | User authentication |
| GET | `/api/scooters` | Yes | List all scooters |
| GET | `/api/scooters/available` | Yes | List available scooters |
| GET | `/api/scooters/{id}` | Yes | Get scooter details |
| GET | `/api/rentals` | Yes | List user rentals |
| GET | `/api/rentals/{id}` | Yes | Get rental details |
| POST | `/api/rentals/start` | Yes | Start new rental |
| POST | `/api/rentals/{id}/end` | Yes | End rental |
| GET | `/api/stats` | Yes | User statistics |

### Data Models

#### Scooter
```json
{
  "id": 1,
  "model": "Scooter Model",
  "license_plate": "SC-001-AB",
  "location": "Location",
  "battery_level": 85,
  "status": "available|in_use|maintenance",
  "created_at": "2026-01-10T10:00:00"
}
```

#### Rental
```json
{
  "id": 1,
  "scooter": {...},
  "start_time": "2026-01-10T11:00:00",
  "end_time": "2026-01-10T11:15:00",
  "status": "active|completed|cancelled",
  "total_cost": 2.70,
  "duration_formatted": "15 Minuten"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check JWT token is valid and included in headers
2. **404 Not Found**: Verify endpoint URL is correct
3. **500 Internal Error**: Check server logs for detailed error information

### Debug Tips

1. Use `-v` flag with curl for verbose output:
   ```bash
   curl -v -X GET https://scoot-rapid-production.up.railway.app/api/health
   ```

2. Check response headers:
   ```bash
   curl -I https://scoot-rapid-production.up.railway.app/api/health
   ```

3. Pretty print JSON responses:
   ```bash
   curl ... | python3 -m json.tool
   ```

## 📞 Support

For API issues or questions:
1. Check the application logs
2. Verify database connectivity
3. Test with the automated test suite
4. Review this documentation for correct endpoints and parameters
