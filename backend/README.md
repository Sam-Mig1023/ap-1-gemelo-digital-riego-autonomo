# VRI Digital Twin FastAPI Backend

Backend service for the Closed-Loop Digital Twin for Autonomous Variable-Rate Irrigation (VRI).

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (or use Docker)
- Redis (or use Docker)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## With Docker Compose

From the project root:

```bash
docker-compose up -d
```

This will start:
- FastAPI backend on `http://localhost:8000`
- React frontend on `http://localhost:3000`
- PostgreSQL + TimescaleDB on port 5432
- Redis on port 6379

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py
│   │       │   ├── fields.py
│   │       │   ├── sensors.py
│   │       │   ├── rl_engine.py
│   │       │   ├── irrigation.py
│   │       │   └── reports.py
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database connection
│   │   └── security.py      # JWT authentication (coming soon)
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── main.py              # Application entry point
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## API Endpoints

### Health Check
- `GET /health` - Health status
- `GET /ready` - Readiness probe

### Agricultural Fields
- `GET /api/v1/fields` - List all fields
- `GET /api/v1/fields/{field_id}` - Get field details
- `GET /api/v1/fields/{field_id}/zones` - Get field zones

### Sensors
- `GET /api/v1/sensors` - List all sensors
- `POST /api/v1/sensors/telemetry/ingest` - Ingest sensor data
- `GET /api/v1/sensors/zone/{zone_id}` - Get zone sensors

### RL Engine
- `POST /api/v1/rl-engine/infer-vri-rates` - Get irrigation recommendation
- `GET /api/v1/rl-engine/decisions` - Get decision history
- `POST /api/v1/rl-engine/decisions/{decision_id}/approve` - Approve decision
- `POST /api/v1/rl-engine/retrain-policy` - Retrain RL model

### Irrigation Control
- `POST /api/v1/irrigation/execute-decision` - Execute irrigation
- `GET /api/v1/irrigation/status` - Get system status
- `GET /api/v1/irrigation/schedule` - Get irrigation schedule

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/history` - Get report history
- `POST /api/v1/reports/schedule` - Schedule periodic reports

## Environment Variables

See `.env.example` for all available options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `RL_MODEL_VERSION` - RL policy version
- `DEBUG` - Enable debug mode

## Development

### Add a new endpoint

1. Create a new file in `app/api/v1/endpoints/`
2. Define the router and endpoints
3. Include in `app/api/v1/__init__.py`

### Database Models

Models should be created in `app/models/` and inherit from `Base`.

## Testing

```bash
pytest
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use a production ASGI server like Gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

3. Configure PostgreSQL, Redis for production
4. Set up SSL/TLS
5. Use environment variable for `SECRET_KEY`

## Monitoring

The backend includes health check endpoints:
- `/health` - Basic health check
- `/ready` - Readiness check for K8s deployments

## Support

For issues or questions about the FastAPI backend, please refer to:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
