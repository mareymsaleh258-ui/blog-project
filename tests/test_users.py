from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token(email, password):
    res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["data"]["access_token"]

def register_user(username, email, password="password123", role="reader"):
    return client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "role": role
    })

def test_create_user():
    res = register_user("testuser", "test@test.com")
    assert res.status_code == 200
    assert res.json()["success"] == True

def test_get_all_users():
    res = client.get("/users/")
    assert res.status_code == 200
    assert res.json()["success"] == True

def test_get_user_by_id():
    create = register_user("testuser2", "test2@test.com")
    user_id = create.json()["data"]["id"]
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 200

def test_get_user_not_found():
    res = client.get("/users/9999")
    assert res.status_code == 404

def test_create_user_duplicate_email():
    register_user("testuser3", "dup@test.com")
    res = register_user("testuser4", "dup@test.com")
    assert res.status_code == 400

def test_update_user():
    create = register_user("testuser5", "test5@test.com", role="admin")
    user_id = create.json()["data"]["id"]
    token = get_token("test5@test.com", "password123")
    res = client.put(f"/users/{user_id}",
        json={"username": "updateduser"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

def test_delete_user():
    register_user("adminuser", "admin@test.com", role="admin")
    token = get_token("admin@test.com", "password123")
    create = register_user("testuser6", "test6@test.com")
    user_id = create.json()["data"]["id"]
    res = client.delete(f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
