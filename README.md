# Overview

The Meeting Scheduler is a full-stack application that allows users to schedule meetings, check availability, and visualize their calendar. It features a modern Streamlit frontend and a FastAPI backend with a PostgreSQL database.

## Features

* **User Authentication:** Secure login with JWT tokens
* **Meeting Management:** Create, view, and manage meetings
* **Calendar Visualization:** Interactive calendar view using `streamlit-calendar`
* **Conflict Detection:** Prevent scheduling conflicts
* **Notifications:** Email/SMS reminders (configurable)
* **Google Calendar Integration:** Sync meetings with Google Calendar
* **Responsive Design:** Works on desktop and mobile devices

## Technology Stack

### Backend

* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0
* **Authentication:** JWT
* **Background Tasks:** AsyncIO
* **Containerization:** Docker

### Frontend

* **Framework:** Streamlit
* **Calendar:** `streamlit-calendar`
* **Styling:** Custom CSS
* **API Communication:** Requests

## Infrastructure

* **Container Orchestration:** Docker Compose
* **Environment Management:** Python dotenv

## Getting Started

### Prerequisites

* Docker and Docker Compose
* Python 3.11+
* PostgreSQL 15
* Redis (for background tasks)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/meeting-scheduler.git
   cd meeting-scheduler
   ```
2. **Set up environment variables:**
   Backend

   ```bash
   echo "POSTGRES_URI=postgresql+asyncpg://user:pass@db:5432/scheduler" > scheduler_api/.env
   echo "JWT_SECRET=your_strong_secret_here" >> scheduler_api/.env
   ```

   Frontend

   ```bash
   echo "API_URL=http://api:8000" > scheduler_ui/.env
   echo "JWT_SECRET=your_strong_secret_here" >> scheduler_ui/.env
   ```
3. **Build and start the application:**

   ```bash
   docker-compose up --build -d
   ```
4. **Apply database migrations:**

   ```bash
   docker-compose exec api alembic upgrade head
   ```
5. **Create a test user (optional):**

   ```bash
   docker-compose exec api python -c "
   from app.crud.user import create_user
   from app.database import get_db
   from app.schemas.user import UserCreate
   import asyncio

   async def init_db():
       async for db in get_db():
           await create_user(db, UserCreate(
               email='test@example.com',
               full_name='Test User',
               password='password123'
           ))

   asyncio.run(init_db())
   ```

## Running Without Docker

1. **Set up the backend:**

   ```bash
   cd scheduler_api
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Set up the frontend:**

   ```bash
   cd ../scheduler_ui
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run streamlit_app.py
   ```

## Accessing the Application

* **Frontend:** `http://localhost:8501`
* **Backend API Docs:** `http://localhost:8000/docs`
* **Adminer (Database GUI):** `http://localhost:8080` (use PostgreSQL server `db`)

## API Endpoints

| Endpoint                | Method | Description              |
| ----------------------- | ------ | ------------------------ |
| `/auth/register`        | POST   | Register a new user      |
| `/auth/login`           | POST   | Authenticate user        |
| `/auth/me`              | GET    | Get current user profile |
| `/meetings/`            | POST   | Create a new meeting     |
| `/meetings/`            | GET    | Get user's meetings      |
| `/availability/{email}` | GET    | Check user availability  |

## Project Structure

```text
meeting-scheduler/
├── scheduler_api/             # FastAPI backend
│   ├── app/                   # Application code
│   │   ├── core/              # Configuration and utilities
│   │   ├── crud/              # Database operations
│   │   ├── models/            # Database models
│   │   ├── routers/           # API endpoints
│   │   ├── schemas/           # Pydantic models
│   │   ├── services/          # Business logic
│   │   ├── tasks/             # Background tasks
│   │   ├── utils/             # Helper functions
│   │   ├── main.py            # Application entry point
│   │   └── dependencies.py    # Dependency injection
│   ├── alembic/               # Database migrations
│   ├── .env                   # Environment variables
│   ├── Dockerfile             # Backend Docker configuration
│   └── requirements.txt       # Python dependencies
│
├── scheduler_ui/              # Streamlit frontend
│   ├── streamlit_app.py       # Main application
   ├── .env                   # Environment variables
   ├── Dockerfile             # Frontend Docker configuration
   └── requirements.txt       # Python dependencies
│
├── docker-compose.yml         # Docker orchestration
├── README.md                  # Project documentation
└── .gitignore                 # Version control ignore rules
```

## Configuration

### Environment Variables

#### Backend (`.env`)

* `POSTGRES_URI`: PostgreSQL connection string
* `JWT_SECRET`: Secret for JWT token generation
* `REDIS_URI`: Redis connection URL
* `SENDGRID_API_KEY`: For email notifications (optional)
* `TWILIO_*`: For SMS notifications (optional)
* `GOOGLE_CLIENT_*`: For Google Calendar integration (optional)

#### Frontend (`.env`)

* `API_URL`: URL of the backend API
* `JWT_SECRET`: Must match backend secret


## Troubleshooting

* **Database connection issues:**

  * Verify PostgreSQL is running
  * Check `.env` file credentials
  * Run `alembic upgrade head`
* **Authentication problems:**

  * Ensure `JWT_SECRET` matches in both services
  * Check token expiration time
* **Docker compose errors:**

  * Run `docker-compose down -v` and rebuild
  * Check port availability (8000, 8501, 5432)
