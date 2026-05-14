from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token(email, password):
    res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["data"]["access_token"]

def test_create_post():
    client.post("/auth/register", json={
        "username": "postauthor",
        "email": "postauthor@test.com",
        "password": "test123",
        "role": "author"
    })
    token = get_token("postauthor@test.com", "test123")
    res = client.post("/posts/", 
        json={"title": "Test Post", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["data"]["title"] == "Test Post"

def test_get_all_posts():
    res = client.get("/posts/")
    assert res.status_code == 200
    assert "posts" in res.json()["data"]

def test_get_post_by_id():
    client.post("/auth/register", json={
        "username": "postauthor2",
        "email": "postauthor2@test.com",
        "password": "test123",
        "role": "author"
    })
    token = get_token("postauthor2@test.com", "test123")
    create = client.post("/posts/",
        json={"title": "Test Post 2", "content": "Content 2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create.json()["data"]["id"]
    res = client.get(f"/posts/{post_id}")
    assert res.status_code == 200

def test_create_post_unauthorized():
    res = client.post("/posts/",
        json={"title": "Test", "content": "Test"}
    )
    assert res.status_code == 401

def test_update_post():
    client.post("/auth/register", json={
        "username": "postauthor3",
        "email": "postauthor3@test.com",
        "password": "test123",
        "role": "author"
    })
    token = get_token("postauthor3@test.com", "test123")
    create = client.post("/posts/",
        json={"title": "Old Title", "content": "Old Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create.json()["data"]["id"]
    res = client.put(f"/posts/{post_id}",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["data"]["title"] == "New Title"

def test_delete_post():
    client.post("/auth/register", json={
        "username": "postauthor4",
        "email": "postauthor4@test.com",
        "password": "test123",
        "role": "author"
    })
    token = get_token("postauthor4@test.com", "test123")
    create = client.post("/posts/",
        json={"title": "Delete Me", "content": "Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create.json()["data"]["id"]
    res = client.delete(f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200


def test_create_post_as_reader():
    client.post("/auth/register", json={
        "username": "readeruser",
        "email": "reader@test.com",
        "password": "test123",
        "role": "reader"
    })
    res = client.post("/auth/login", json={
        "email": "reader@test.com",
        "password": "test123"
    })
    token = res.json()["data"]["access_token"]

    res = client.post("/posts/",
        json={"title": "Test", "content": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403