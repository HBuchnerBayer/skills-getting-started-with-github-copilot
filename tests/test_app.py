"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {}
    for name, details in activities.items():
        original_activities[name] = {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
    
    yield
    
    # Restore original state after test
    for name, details in original_activities.items():
        activities[name] = details


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesAPI:
    """Tests for the GET /api/activities endpoint"""
    
    def test_get_activities_returns_list(self, client):
        """Test that /api/activities returns a list of activities"""
        response = client.get("/api/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity contains required fields"""
        response = client.get("/api/activities")
        data = response.json()
        
        required_fields = ["id", "name", "description", "schedule", "max_participants", "current_participants"]
        for activity in data:
            for field in required_fields:
                assert field in activity
    
    def test_get_activities_participant_count(self, client):
        """Test that current_participants count is accurate"""
        response = client.get("/api/activities")
        data = response.json()
        
        for activity in data:
            activity_name = activity["id"]
            expected_count = len(activities[activity_name]["participants"])
            assert activity["current_participants"] == expected_count


class TestGetActivityParticipants:
    """Tests for the GET /api/activities/{activity_id}/participants endpoint"""
    
    def test_get_participants_for_valid_activity(self, client):
        """Test getting participants for a valid activity"""
        response = client.get("/api/activities/Soccer Team/participants")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Check that each participant has an email field
        for participant in data:
            assert "email" in participant
    
    def test_get_participants_returns_correct_emails(self, client):
        """Test that returned participants match the activity data"""
        activity_id = "Soccer Team"
        response = client.get(f"/api/activities/{activity_id}/participants")
        data = response.json()
        
        expected_emails = activities[activity_id]["participants"]
        returned_emails = [p["email"] for p in data]
        
        assert set(returned_emails) == set(expected_emails)
    
    def test_get_participants_for_invalid_activity(self, client):
        """Test getting participants for non-existent activity"""
        response = client.get("/api/activities/NonExistent Activity/participants")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns activities dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Soccer Team" in data
        assert "Basketball Club" in data


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Soccer Team"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        email = "alex@mergington.edu"  # Already in Soccer Team
        
        response = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_for_invalid_activity(self, client):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/NonExistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterParticipant:
    """Tests for the DELETE /api/activities/{activity_id}/participants/{email} endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        activity_id = "Soccer Team"
        email = "alex@mergington.edu"
        
        # Verify participant exists before deletion
        assert email in activities[activity_id]["participants"]
        
        response = client.delete(f"/api/activities/{activity_id}/participants/{email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify participant was removed
        assert email not in activities[activity_id]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant not in the activity"""
        response = client.delete(
            "/api/activities/Soccer Team/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_from_invalid_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/api/activities/NonExistent Activity/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_and_signup_again(self, client):
        """Test that a participant can be unregistered and re-registered"""
        activity_id = "Basketball Club"
        email = "james@mergington.edu"
        
        # Unregister
        response = client.delete(f"/api/activities/{activity_id}/participants/{email}")
        assert response.status_code == 200
        assert email not in activities[activity_id]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/{activity_id}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity_id]["participants"]


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_complete_participant_lifecycle(self, client):
        """Test the complete lifecycle of a participant"""
        activity_id = "Chess Club"
        new_email = "testuser@mergington.edu"
        
        # 1. Get initial participant count
        response = client.get(f"/api/activities/{activity_id}/participants")
        initial_count = len(response.json())
        
        # 2. Sign up
        response = client.post(f"/activities/{activity_id}/signup?email={new_email}")
        assert response.status_code == 200
        
        # 3. Verify participant was added
        response = client.get(f"/api/activities/{activity_id}/participants")
        participants = response.json()
        assert len(participants) == initial_count + 1
        assert any(p["email"] == new_email for p in participants)
        
        # 4. Unregister
        response = client.delete(f"/api/activities/{activity_id}/participants/{new_email}")
        assert response.status_code == 200
        
        # 5. Verify participant was removed
        response = client.get(f"/api/activities/{activity_id}/participants")
        participants = response.json()
        assert len(participants) == initial_count
        assert not any(p["email"] == new_email for p in participants)
