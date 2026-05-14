from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_success():
    res = client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "test123",
        "role": "author"
    })
    assert res.status_code == 200
    assert res.json()["success"] == True

def test_register_duplicate_email():
    client.post("/auth/register", json={
        "username": "dupuser",
        "email": "dup@test.com",
        "password": "test123",
        "role": "reader"
    })
    res = client.post("/auth/register", json={
        "username": "dupuser2",
        "email": "dup@test.com",
        "password": "test123",
        "role": "reader"
    })
    assert res.status_code == 400

def test_login_success():
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@test.com",
        "password": "test123",
        "role": "author"
    })
    res = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "test123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()["data"]

def test_login_wrong_password():
    res = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401