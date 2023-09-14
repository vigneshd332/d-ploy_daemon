"""
Docker Tests
"""

from fastapi.testclient import TestClient
from requests import Response

from dploy_daemon.main import app

client = TestClient(app)
container_id: str = ""


def test_docker_container_create() -> None:
    """Docker Container Create Test"""
    response: Response = client.post("/docker/containers/create", json={
        "image": "busybox:latest",
        "name": "test_container",
    })
    assert response.status_code == 200
    response = response.json()
    assert response["status"] == "created"
    assert response["name"] == "test_container"

    global container_id
    container_id = response["id"]


def test_docker_container_info() -> None:
    """Docker Container Info Test"""
    response: Response = client.get(f"/docker/containers/{container_id}")
    assert response.status_code == 200
    response = response.json()
    assert response["id"] == container_id
    assert response["name"] == "test_container"


def test_docker_container_start() -> None:
    """Docker Container Start Test"""
    response: Response = client.post(
        f"/docker/containers/{container_id}/start")
    assert response.status_code == 200
    response = response.json()
    assert response["message"] == f"Container {container_id} started"


def test_docker_container_stop() -> None:
    """Docker Container Stop Test"""
    response: Response = client.post(f"/docker/containers/{container_id}/stop")
    assert response.status_code == 200
    response = response.json()
    assert response["message"] == f"Container {container_id} stopped"


def test_container_restart() -> None:
    """Docker Container Restart Test"""
    response: Response = client.post(
        f"/docker/containers/{container_id}/restart")
    assert response.status_code == 200
    response = response.json()
    assert response["message"] == f"Container {container_id} restarted"


def test_container_kill() -> None:
    """Docker Container Kill Test"""
    response: Response = client.post(
        f"/docker/containers/{container_id}/kill")
    assert response.status_code == 403


def test_container_delete() -> None:
    """Docker Container Delete Test"""
    response: Response = client.post(
        f"/docker/containers/delete", json={
            "container_id": container_id,
            "force": True,
            "v": True
        })
    assert response.status_code == 200
    response = response.json()
    assert response["message"] == f"Container {container_id} deleted"
