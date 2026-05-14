from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def register_and_login(username, email):
    client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "test123",
        "role": "author"
    })
    res = client.post("/auth/login", json={
        "email": email,
        "password": "test123"
    })
    return res.json()["data"]["access_token"]

def test_create_comment():
    token = register_and_login("commentuser1", "comment1@test.com")
    post = client.post("/posts/",
        json={"title": "Post for comment", "content": "Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = post.json()["data"]["id"]
    res = client.post("/comments/",
        json={"content": "تعليق تجريبي", "post_id": post_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] == True

def test_get_comments_by_post():
    token = register_and_login("commentuser2", "comment2@test.com")
    post = client.post("/posts/",
        json={"title": "Post 2", "content": "Content 2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = post.json()["data"]["id"]
    client.post("/comments/",
        json={"content": "تعليق", "post_id": post_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    res = client.get(f"/comments/post/{post_id}")
    assert res.status_code == 200

def test_nested_comment():
    token = register_and_login("commentuser3", "comment3@test.com")
    post = client.post("/posts/",
        json={"title": "Post 3", "content": "Content 3"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = post.json()["data"]["id"]
    parent = client.post("/comments/",
        json={"content": "تعليق رئيسي", "post_id": post_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    parent_id = parent.json()["data"]["id"]
    res = client.post("/comments/",
        json={"content": "رد على التعليق", "post_id": post_id, "parent_id": parent_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

def test_update_comment():
    token = register_and_login("commentuser4", "comment4@test.com")
    post = client.post("/posts/",
        json={"title": "Post 4", "content": "Content 4"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = post.json()["data"]["id"]
    comment = client.post("/comments/",
        json={"content": "قديم", "post_id": post_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    comment_id = comment.json()["data"]["id"]
    res = client.put(f"/comments/{comment_id}",
        json={"content": "جديد"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

def test_delete_comment():
    token = register_and_login("commentuser5", "comment5@test.com")
    post = client.post("/posts/",
        json={"title": "Post 5", "content": "Content 5"},
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = post.json()["data"]["id"]
    comment = client.post("/comments/",
        json={"content": "هيتمسح", "post_id": post_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    comment_id = comment.json()["data"]["id"]
    res = client.delete(f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

def test_create_comment_unauthorized():
    res = client.post("/comments/",
        json={"content": "تعليق", "post_id": 1}
    )
    assert res.status_code == 401