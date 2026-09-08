import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage.memory import agents, comments, tickets


@pytest.fixture
def client():
    with TestClient(app) as c:
        tickets.clear()
        comments.clear()
        agents.clear()
        yield c


@pytest.fixture
def ticket_id(client):
    response = client.post(
        "/tickets",
        json={
            "title": "Terminal sin conexion",
            "description": "La terminal de la caja 2 perdio conexion con el servidor.",
            "priority": "high",
            "requester_email": "tienda0500@retail.example",
        },
    )
    return response.json()["id"]
