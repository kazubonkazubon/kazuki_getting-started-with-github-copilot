import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_returns_all_activities_with_correct_structure(self):
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Based on current activities
        
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

class TestPostSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup_adds_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_duplicate_signup_returns_error(self):
        # Arrange
        activity_name = "Programming Class"
        email = "duplicate@mergington.edu"
        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Second signup with same email
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_to_nonexistent_activity_returns_404(self):
        # Arrange
        nonexistent_activity = "Fake Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

class TestDeleteSignup:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_successful_unregister_removes_participant(self):
        # Arrange
        activity_name = "Gym Class"
        email = "temp@mergington.edu"
        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_non_participant_returns_error(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self):
        # Arrange
        nonexistent_activity = "Fake Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
