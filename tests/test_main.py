"""
Tests for miscellaneous routes defined in main.py
"""

from fastapi.testclient import TestClient

from dploy_daemon.main import app

client = TestClient(app)


def test_root() -> None:
    """Test root route"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "D-Ploy Daemon is running!"
    }
