import pytest


@pytest.fixture
def agent_email(client):
    response = client.post(
        "/agents",
        json={"name": "Ana Rivera", "email": "ana.rivera@helpdesk.example", "team": "infra"},
    )
    return response.json()["email"]


def test_assign_ticket(client, ticket_id, agent_email):
    response = client.post(f"/tickets/{ticket_id}/assign", json={"agent_email": agent_email})
    assert response.status_code == 200
    assert response.json()["assigned_to"] == agent_email


def test_assign_unknown_agent(client, ticket_id):
    response = client.post(f"/tickets/{ticket_id}/assign", json={"agent_email": "nadie@helpdesk.example"})
    assert response.status_code == 404


def test_closed_ticket_cannot_be_assigned(client, ticket_id, agent_email):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    response = client.post(f"/tickets/{ticket_id}/assign", json={"agent_email": agent_email})
    assert response.status_code == 409


def test_unassign_ticket(client, ticket_id, agent_email):
    client.post(f"/tickets/{ticket_id}/assign", json={"agent_email": agent_email})
    response = client.delete(f"/tickets/{ticket_id}/assign")
    assert response.status_code == 200
    assert response.json()["assigned_to"] is None


def test_unassign_unassigned_ticket(client, ticket_id):
    assert client.delete(f"/tickets/{ticket_id}/assign").status_code == 409
