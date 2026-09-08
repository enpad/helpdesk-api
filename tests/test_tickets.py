def test_create_ticket(client):
    response = client.post(
        "/tickets",
        json={
            "title": "No abre el cajon de dinero",
            "description": "El cajon no abre al finalizar la venta en la caja 1.",
            "priority": "medium",
            "requester_email": "tienda0101@retail.example",
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "open"


def test_get_ticket(client, ticket_id):
    assert client.get(f"/tickets/{ticket_id}").status_code == 200


def test_get_missing_ticket(client):
    response = client.get("/tickets/no-existe")
    assert response.status_code == 404
    assert "error" in response.json()


def test_update_title(client, ticket_id):
    response = client.patch(f"/tickets/{ticket_id}", json={"title": "Terminal sin conexion (actualizado)"})
    assert response.status_code == 200
    assert response.json()["title"] == "Terminal sin conexion (actualizado)"


def test_update_priority(client, ticket_id):
    response = client.patch(f"/tickets/{ticket_id}", json={"priority": "critical"})
    assert response.status_code == 200
    assert response.json()["priority"] == "critical"


def test_close_ticket(client, ticket_id):
    response = client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    assert response.status_code == 200
    assert response.json()["status"] == "closed"


def test_closed_ticket_cannot_be_edited(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    response = client.patch(f"/tickets/{ticket_id}", json={"title": "Otro titulo distinto"})
    assert response.status_code == 409


def test_closed_ticket_cannot_be_deleted(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    assert client.delete(f"/tickets/{ticket_id}").status_code == 409


def test_closed_ticket_can_still_be_read(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    assert client.get(f"/tickets/{ticket_id}").status_code == 200


def test_closed_ticket_can_be_reopened(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    response = client.patch(f"/tickets/{ticket_id}", json={"status": "open"})
    assert response.status_code == 200
    assert response.json()["status"] == "open"


def test_closed_ticket_reopen_with_extra_field_still_conflicts(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    response = client.patch(
        f"/tickets/{ticket_id}", json={"status": "open", "title": "Otro titulo distinto"}
    )
    assert response.status_code == 409


def test_delete_open_ticket(client, ticket_id):
    assert client.delete(f"/tickets/{ticket_id}").status_code == 204


def test_list_filters_by_status(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "in_progress"})
    response = client.get("/tickets", params={"status": "in_progress"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_stats_summary(client, ticket_id):
    response = client.get("/tickets/stats/summary")
    assert response.status_code == 200
    assert response.json()["total"] == 1
