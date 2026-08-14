# SafeStation AI — Backend (Flask API)

Abimbola's primary area. Flask API that serves incident data to the dashboard.

## Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Endpoints needed
- GET /api/incidents — list all incidents from Cosmos DB
- GET /api/incidents/<id> — single incident detail
- GET /api/telemetry — recent telemetry readings
- POST /api/incidents/<id>/review — human review approval/rejection
- GET /api/health — system health check

## Environment variables
Copy ../.env.example and fill in Cosmos DB credentials.
