from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

# Import models to ensure they are registered with Base metadata before creation
from app.db.database import Base, engine
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance

from app.api import auth, admin, student, events

# Initialize database tables
Base.metadata.create_all(bind=engine) 

app = FastAPI(
    title="Event Ticket & Attendance Tracking API",
    description="High-fidelity backend supporting event ticketing and QR-code attendance verification synced to Google Sheets.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registrations
# 1. Auth routes at /auth/* (standard JWT Flow)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 2. Auth routes at /* (supports direct root-level calls like /register and /login from frontend)
app.include_router(auth.router, tags=["Authentication Root Fallbacks"])

# 3. Admin endpoints at /admin/*
app.include_router(admin.router, prefix="/admin", tags=["Admin Actions"])

# 4. Student endpoints at /student/*
app.include_router(student.router, prefix="/student", tags=["Student Actions"])

# 5. Shared events details at /events/*
app.include_router(events.router, prefix="/events", tags=["Shared Events"])

@app.get("/", tags=["General"])
def home(): 
    return {
        "status": "online",
        "system": "RTU Event Ticket Attendance Tracking Website"
    }