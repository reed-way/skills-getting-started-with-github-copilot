import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    # Arrange
    expected_keys = set(activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert set(result.keys()) == expected_keys
    assert "Chess Club" in result
    assert result["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    initial_participants = list(activities[activity_name]["participants"])

    try:
        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1
    finally:
        activities[activity_name]["participants"] = initial_participants


def test_duplicate_signup_raises_400():
    # Arrange
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    # Arrange
    activity_name = "Gym Class"
    email = activities[activity_name]["participants"][0]
    initial_participants = list(activities[activity_name]["participants"])

    try:
        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(initial_participants) - 1
    finally:
        activities[activity_name]["participants"] = initial_participants


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Art Studio"
    email = "doesnotexist@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
