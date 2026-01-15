"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Soccer Team": {
        "description": "Join the school soccer team and compete in inter-school matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["alex@mergington.edu", "ryan@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and participate in friendly tournaments",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu", "lucas@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore various art mediums including painting, drawing, and sculpture",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["emily@mergington.edu", "ava@mergington.edu"]
    },
    "Drama Club": {
        "description": "Participate in theatrical productions and develop acting skills",
        "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking through competitive debates",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["william@mergington.edu", "noah@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Prepare for science competitions and conduct experiments",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "liam@mergington.edu"]
    },
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/activities")
def get_activities_api():
    """Get all activities with their details formatted for the frontend"""
    activities_list = []
    for name, details in activities.items():
        activities_list.append({
            "id": name,
            "name": name,
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "current_participants": len(details["participants"])
        })
    return activities_list


@app.get("/api/activities/{activity_id}/participants")
def get_activity_participants(activity_id: str):
    """Get the list of participants for a specific activity"""
    if activity_id not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = activities[activity_id]
    return [{"email": email} for email in activity["participants"]]


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/api/activities/{activity_id}/participants/{email}")
def unregister_participant(activity_id: str, email: str):
    """Unregister a participant from an activity"""
    if activity_id not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = activities[activity_id]
    
    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")
    
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_id}"}
