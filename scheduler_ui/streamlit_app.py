import streamlit as st
import requests
import os
import jwt
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import time

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "your_strong_secret_here")

st.set_page_config(
        page_title="Meeting Scheduler", 
        page_icon="📅", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS for styling
st.markdown("""
<style>
    /* Main page styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Login container */
    .login-container {
        max-width: 400px;
        padding: 30px;
        margin: 100px auto 0;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        border: none;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #3a7bc8;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Header styling */
    .header {
        padding-bottom: 1rem;
        border-bottom: 1px solid #eaeaea;
        margin-bottom: 1.5rem;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Calendar styling */
    .fc-event {
        cursor: pointer;
        font-size: 0.9em;
        border-radius: 4px;
    }
    
    /* Form styling */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stDateInput>div>div>input, 
    .stTimeInput>div>div>input {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def get_auth_token(email, password):
    """Authenticate user and return JWT token"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    return None

def fetch_meetings(start_date=None, end_date=None):
    """Fetch meetings from the backend API"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        
        params = {}
        if start_date and end_date:
            params = {
                "start": start_date.isoformat() + "Z",
                "end": end_date.isoformat() + "Z"
            }
        
        response = requests.get(
            f"{API_URL}/meetings/",
            headers=headers,
            params=params
        )
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Error fetching meetings: {str(e)}")
        return []

def create_meeting(meeting_data):
    """Create a new meeting"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/meetings/", 
            json=meeting_data, 
            headers=headers
        )
        return response
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def update_meeting(meeting_id, meeting_data):
    """Update an existing meeting"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{API_URL}/meetings/{meeting_id}", 
            json=meeting_data, 
            headers=headers
        )
        return response
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def delete_meeting(meeting_id):
    """Delete a meeting"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.delete(
            f"{API_URL}/meetings/{meeting_id}", 
            headers=headers
        )
        return response
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# --- Add helpers for session persistence ---
def persist_session():
    st.experimental_set_query_params(
        token=st.session_state.get("token", ""),
        logged_in=str(st.session_state.get("logged_in", False)),
        user_email=st.session_state.get("user_email", "")
    )

def restore_session():
    params = st.experimental_get_query_params()
    if params.get("token"):
        st.session_state.token = params["token"][0]
    if params.get("logged_in"):
        st.session_state.logged_in = params["logged_in"][0] == "True"
    if params.get("user_email"):
        st.session_state.user_email = params["user_email"][0]

def transform_meetings_to_events(meetings):
    """Transform backend meetings to calendar events"""
    events = []
    for meeting in meetings:
        events.append({
            "id": meeting["id"],  # Use 'id' for calendar event
            "title": meeting["title"],
            "start": meeting["start_time"],
            "end": meeting["end_time"],
            "color": "#4a90e2",
            "extendedProps": {
                "description": meeting.get("description", ""),
                "location": meeting.get("location", ""),
                "attendees": ", ".join([a["email"] for a in meeting.get("attendees", [])])
            }
        })
    return events

def show_login_page():
    """Display login form"""
    st.markdown(
        f'<div class="login-container">'
        f'  <h2 style="text-align: center; margin-bottom: 30px;">Meeting Scheduler</h2>'
        f'  <p style="text-align: center; color: #666; margin-bottom: 30px;">Please login to access your schedule</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                token = get_auth_token(email, password)
                if token:
                    st.session_state.token = token
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.success("Login successful!")
                    persist_session()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid email or password")

def show_main_dashboard():
    # Initialize calendar refresh counter
    if "calendar_refresh" not in st.session_state:
        st.session_state.calendar_refresh = 0
    # Force refresh logic
    if st.session_state.get("force_refresh"):
        st.session_state.pop("force_refresh")
        st.experimental_rerun()
    # Initialize session state variables
    if 'calendar_view' not in st.session_state:
        st.session_state.calendar_view = "dayGridMonth"
    
    if 'selected_meeting' not in st.session_state:
        st.session_state.selected_meeting = None
    
    # Dashboard header
    st.markdown(
        f'<div class="header">'
        f'  <h1 style="margin-bottom: 0;">Meeting Dashboard</h1>'
        f'  <p style="color: #666; margin-top: 0;">Welcome back, {st.session_state.user_email}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Create two columns
    col1, col2 = st.columns([3, 2], gap="large")
    
    # Left column - Calendar
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Meeting Calendar")
        
        # Calendar view selector
        view_options = ["dayGridMonth", "timeGridWeek", "timeGridDay", "listWeek"]
        selected_view = st.selectbox(
            "Calendar View", 
            view_options, 
            index=view_options.index(st.session_state.calendar_view),
            key="calendar_view_select"
        )
        st.session_state.calendar_view = selected_view
        
        # Calendar configuration
        calendar_options = {
            "editable": "false",
            "selectable": "true",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": ""
            },
            "initialView": st.session_state.calendar_view,
            "navLinks": "true",
        }
        
        # Fetch meetings for the current month
        today = datetime.utcnow()
        first_day = today.replace(day=1)
        last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        meetings = fetch_meetings(first_day, last_day)
        events = transform_meetings_to_events(meetings)
        
        # Display the calendar
        calendar_result = calendar(
            events=events,
            options=calendar_options,
            custom_css="""
            .fc-event {
                cursor: pointer;
                padding: 4px 8px;
            }
            .fc-daygrid-event-dot {
                display: none;
            }
            """,
            key=f"calendar_{st.session_state.calendar_refresh}"
        )
        
        # Show meeting details when an event is clicked
        if calendar_result.get("eventClick"):
            event = calendar_result["eventClick"]["event"]
            st.session_state.selected_meeting = event
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close card
    
    # Right column - Create Meeting Form
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Schedule New Meeting")
        
        with st.form("meeting_form", clear_on_submit=True):
            title = st.text_input("Title", max_chars=100)
            description = st.text_area("Description", max_chars=500, height=100)
            location = st.text_input("Location", max_chars=100)
            
            col_start, col_end = st.columns(2)
            with col_start:
                start_time = st.date_input("Start Date", min_value=datetime.today())
                start_time_time = st.time_input("Start Time")
            with col_end:
                end_time = st.date_input("End Date", min_value=datetime.today())
                end_time_time = st.time_input("End Time")
            
            # Combine date and time
            start_datetime = datetime.combine(start_time, start_time_time)
            end_datetime = datetime.combine(end_time, end_time_time)
            
            # Get available users (in a real app, fetch from backend)
            available_users = [
                "user1@example.com", 
                "user2@example.com", 
                "user3@example.com",
                st.session_state.user_email
            ]
            attendees = st.multiselect("Attendees", available_users, default=[st.session_state.user_email])
            
            if st.form_submit_button("Schedule Meeting"):
                if not title:
                    st.error("Title is required")
                elif start_datetime >= end_datetime:
                    st.error("End time must be after start time")
                else:
                    meeting_data = {
                        "title": title,
                        "description": description,
                        "start_time": start_datetime.isoformat() + "Z",
                        "end_time": end_datetime.isoformat() + "Z",
                        "location": location,
                        "attendee_emails": attendees
                    }
                    response = create_meeting(meeting_data)
                    if response and response.status_code == 201:
                        st.success("Meeting scheduled successfully!")
                        persist_session()
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        error = "Unknown error"
                        if response:
                            error = response.json().get("detail", "Unknown error")
                        st.error(f"Error scheduling meeting: {error}")
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close card
    
    # Selected Meeting Details
    if st.session_state.selected_meeting:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Meeting Details")
        
        event = st.session_state.selected_meeting
        meeting_id = event.get("id")  # Use 'id' instead of 'resourceId'
        
        # Create tabs for view and edit
        tab1, tab2 = st.tabs(["View", "Edit"])
        
        with tab1:
            st.write(f"**Title:** {event['title']}")
            st.write(f"**Start:** {event['start']}")
            st.write(f"**End:** {event['end']}")
            
            if event.get("extendedProps", {}).get("description"):
                st.write(f"**Description:** {event['extendedProps']['description']}")
            if event.get("extendedProps", {}).get("location"):
                st.write(f"**Location:** {event['extendedProps']['location']}")
            if event.get("extendedProps", {}).get("attendees"):
                st.write(f"**Attendees:** {event['extendedProps']['attendees']}")
        
        with tab2:
            with st.form("edit_meeting_form"):
                # Parse datetime strings
                start_dt = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                
                # Form fields
                edit_title = st.text_input("Title", value=event['title'], max_chars=100)
                edit_description = st.text_area("Description", value=event.get("extendedProps", {}).get("description", ""), max_chars=500, height=100)
                edit_location = st.text_input("Location", value=event.get("extendedProps", {}).get("location", ""), max_chars=100)
                
                col_start, col_end = st.columns(2)
                with col_start:
                    edit_start_date = st.date_input("Start Date", value=start_dt.date())
                    edit_start_time = st.time_input("Start Time", value=start_dt.time())
                with col_end:
                    edit_end_date = st.date_input("End Date", value=end_dt.date())
                    edit_end_time = st.time_input("End Time", value=end_dt.time())
                
                # Get current attendees
                current_attendees = event.get("extendedProps", {}).get("attendees", "").split(", ") if event.get("extendedProps", {}).get("attendees") else []
                
                # Get available users
                available_users = [
                    "user1@example.com", 
                    "user2@example.com", 
                    "user3@example.com",
                    st.session_state.user_email
                ]
                edit_attendees = st.multiselect("Attendees", available_users, default=current_attendees)
                
                col_save, col_delete, col_cancel = st.columns(3)
                
                with col_save:
                    if st.form_submit_button("Save Changes"):
                        # Combine date and time
                        new_start_datetime = datetime.combine(edit_start_date, edit_start_time)
                        new_end_datetime = datetime.combine(edit_end_date, edit_end_time)
                        
                        if new_start_datetime >= new_end_datetime:
                            st.error("End time must be after start time")
                        else:
                            meeting_data = {
                                "id": meeting_id,
                                "title": edit_title,
                                "description": edit_description,
                                "start_time": new_start_datetime.isoformat() + "Z",
                                "end_time": new_end_datetime.isoformat() + "Z",
                                "location": edit_location,
                                "attendee_emails": edit_attendees
                            }
                            response = update_meeting(meeting_id, meeting_data)
                            if response and response.status_code == 200:
                                st.success("Meeting updated successfully!")
                                st.session_state.selected_meeting = None
                                st.session_state.calendar_refresh += 1
                                persist_session()
                                time.sleep(1)
                                st.experimental_rerun()
                            else:
                                error = "Unknown error"
                                if response:
                                    error = response.json().get("detail", "Unknown error")
                                st.error(f"Error updating meeting: {error}")
                
                with col_delete:
                    if st.form_submit_button("Delete Meeting", type="secondary"):
                        response = delete_meeting(meeting_id)
                        if response and response.status_code == 204:
                            st.success("Meeting deleted successfully!")
                            st.session_state.selected_meeting = None
                            st.session_state.calendar_refresh += 1
                            persist_session()
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            error = "Unknown error"
                            if response:
                                error = response.json().get("detail", "Unknown error")
                            st.error(f"Error deleting meeting: {error}")
                
                with col_cancel:
                    if st.form_submit_button("Cancel"):
                        st.session_state.selected_meeting = None
                        st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close card
    
    # Logout button
    st.sidebar.markdown(f"Logged in as: **{st.session_state.user_email}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.user_email = None
        st.session_state.selected_meeting = None
        persist_session()
        st.success("Logged out successfully!")
        time.sleep(1)
        st.experimental_rerun()

# Main app logic
def main():
    
    # Restore session from query params on first load
    restore_session()
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.user_email = None
    
    # Show appropriate page based on login state
    if st.session_state.logged_in:
        show_main_dashboard()
    else:
        show_login_page()

# if __name__ == "__main__":
#     st.set_page_config(
#         page_title="Meeting Scheduler", 
#         page_icon="📅", 
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
main()