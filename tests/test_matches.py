def test_create_match(client):
    response = client.post("/matches/", json={"team_a": "India", "team_b": "Australia"})
    assert response.status_code == 200
    data = response.json()
    assert data["team_a"] == "India"
    assert data["team_b"] == "Australia"
    assert data["status"] == "SCHEDULED"


def test_get_match(client):
    create_resp = client.post("/matches/", json={"team_a": "England", "team_b": "Pakistan"})
    match_id = create_resp.json()["id"]

    response = client.get(f"/matches/{match_id}")
    assert response.status_code == 200
    assert response.json()["team_a"] == "England"


def test_get_match_not_found(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/matches/{fake_id}")
    assert response.status_code == 404


def test_list_matches(client):
    client.post("/matches/", json={"team_a": "SA", "team_b": "NZ"})
    client.post("/matches/", json={"team_a": "SL", "team_b": "WI"})

    response = client.get("/matches/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_score_moves_to_live(client):
    create_resp = client.post("/matches/", json={"team_a": "India", "team_b": "SA"})
    match_id = create_resp.json()["id"]

    response = client.patch(f"/matches/{match_id}/score", json={"score_a": 50, "score_b": 30})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "LIVE"
    assert data["score_a"] == 50


def test_cannot_update_score_after_completed(client):
    create_resp = client.post("/matches/", json={"team_a": "India", "team_b": "England"})
    match_id = create_resp.json()["id"]

    client.patch(f"/matches/{match_id}/complete")

    response = client.patch(f"/matches/{match_id}/score", json={"score_a": 100, "score_b": 90})
    assert response.status_code == 400
    assert "completed" in response.json()["detail"].lower()


def test_delete_match(client):
    create_resp = client.post("/matches/", json={"team_a": "Aus", "team_b": "NZ"})
    match_id = create_resp.json()["id"]

    response = client.delete(f"/matches/{match_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/matches/{match_id}")
    assert get_resp.status_code == 404