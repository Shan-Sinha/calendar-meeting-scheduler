from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from schemas.meeting import Meeting
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarAdapter:
    def __init__(self, credentials: dict):
        self.creds = Credentials.from_authorized_user_info(credentials)
        self.service = build('calendar', 'v3', credentials=self.creds)

    async def create_event(self, meeting: Meeting):
        event = {
            'summary': meeting.title,
            'description': meeting.description,
            'start': {'dateTime': meeting.start_time.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': meeting.end_time.isoformat(), 'timeZone': 'UTC'},
            'attendees': [{'email': email} for email in meeting.attendee_emails],
            'location': meeting.location,
            'reminders': {'useDefault': True}
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            return created_event['id']
        except Exception as e:
            logger.error(f"Google Calendar error: {e}")
            return None