def test_add_comment(client, ticket_id):
    response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"author": "ana.rivera@helpdesk.example", "body": "Revisando el cableado de red."},
    )
    assert response.status_code == 201


def test_list_comments(client, ticket_id):
    client.post(f"/tickets/{ticket_id}/comments", json={"author": "ana", "body": "Primera nota"})
    client.post(f"/tickets/{ticket_id}/comments", json={"author": "luis", "body": "Segunda nota"})
    response = client.get(f"/tickets/{ticket_id}/comments")
    assert len(response.json()) == 2


def test_closed_ticket_rejects_comments(client, ticket_id):
    client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    response = client.post(f"/tickets/{ticket_id}/comments", json={"author": "ana", "body": "Nota tardia"})
    assert response.status_code == 409


def test_comment_on_missing_ticket(client):
    response = client.post("/tickets/no-existe/comments", json={"author": "ana", "body": "Nota"})
    assert response.status_code == 404
