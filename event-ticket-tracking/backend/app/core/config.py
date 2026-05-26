import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7d44bc4a796e67617b07e8ef6e61a6c4b2a472c695a7201c7d2354c01d9cdb07")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Google Sheets Integration
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "Event Attendance Tracking")
    
    # n8n Automation Webhook Placeholder
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "")

settings = Settings()
