import logging
import os
from app.core.config import settings

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("attendance_sheets")

try:
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    gspread = None
    GSPREAD_AVAILABLE = False
    logger.warning("gspread module not installed. Google Sheets synchronization will run in simulation mode.")

def sync_attendance_to_sheets(
    student_name: str, 
    student_number: str, 
    department: str, 
    course: str, 
    event_title: str, 
    time_in: str
) -> bool:
    """
    Syncs a single attendance record to a Google Sheet.
    If the credentials.json file or the gspread library does not exist, it falls back to a graceful simulation log.
    """
    creds_path = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
    sheet_name = settings.GOOGLE_SHEET_NAME

    if not GSPREAD_AVAILABLE or not os.path.exists(creds_path):
        logger.warning(
            f"[Google Sheets Simulation] " + ("Library 'gspread' is missing. " if not GSPREAD_AVAILABLE else "") + 
            f"Would sync to Sheet '{sheet_name}':\n"
            f"  - Name: {student_name}\n"
            f"  - Student ID: {student_number or 'N/A'}\n"
            f"  - Department: {department or 'N/A'}\n"
            f"  - Course: {course or 'N/A'}\n"
            f"  - Event: {event_title}\n"
            f"  - Time In: {time_in}\n"
            f"Install 'gspread' and place your credentials at: {os.path.abspath(creds_path)} to enable live sync."
        )
        return False

    try:
        # Authenticate using modern built-in gspread service account auth
        gc = gspread.service_account(filename=creds_path)
        
        # Open the spreadsheet
        try:
            sh = gc.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            logger.info(f"Google Sheet '{sheet_name}' not found. Creating a new one...")
            sh = gc.create(sheet_name)
            # Share with anyone or keep it private. The service account owns it.
            # Usually, you need to share it with your personal email to view it.
            logger.info(f"New sheet created. Remember to share sheet access with your email in your Google Cloud Console.")
        
        # Get first worksheet
        worksheet = sh.get_worksheet(0)
        if not worksheet:
            worksheet = sh.add_worksheet(title="Attendance Log", rows="100", cols="10")
            
        # Check if worksheet is brand new/empty to add header
        headers = ["Student Name", "Student Number", "Department", "Course", "Event Title", "Time In"]
        existing_values = worksheet.get_all_values()
        if not existing_values or len(existing_values) == 0:
            worksheet.append_row(headers)
            
        # Append the new attendance row
        row_data = [
            student_name, 
            student_number or "N/A", 
            department or "N/A", 
            course or "N/A", 
            event_title, 
            time_in
        ]
        worksheet.append_row(row_data)
        logger.info(f"Successfully synced attendance for student '{student_name}' to Google Sheet '{sheet_name}'.")
        return True

    except Exception as e:
        logger.error(
            f"[Google Sheets Error] Could not sync attendance for {student_name}: {str(e)}\n"
            f"Check if credentials.json is valid and the Service Account has sheet permissions."
        )
        return False
