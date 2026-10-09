import pytest
from fastapi.testclient import TestClient
from app.main import app, sync_db_to_trie
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_app():
    init_db()
    sync_db_to_trie()

@pytest.fixture
def client():
    return TestClient(app)

def test_get_all_words(client):
    response = client.get("/api/words")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_crud_word_lifecycle(client):
    # 1. Create (POST)
    new_word = {
        "word": "pytest",
        "meaning": "framework kiem thu",
        "part_of_speech": "noun",
        "example": "Testing with pytest is fast"
    }
    res_post = client.post("/api/words", json=new_word)
    assert res_post.status_code == 201
    word_id = res_post.json()["id"]
    assert res_post.json()["word"] == "pytest"

    # 2. Duplicate Check
    res_dup = client.post("/api/words", json=new_word)
    assert res_dup.status_code == 409

    # 3. Update (PUT)
    res_put = client.put(f"/api/words/{word_id}", json={"meaning": "thu vien test python"})
    assert res_put.status_code == 200
    assert res_put.json()["meaning"] == "thu vien test python"

    # 4. Delete (DELETE)
    res_del = client.delete(f"/api/words/{word_id}")
    assert res_del.status_code == 200

    # 5. Verify Deletion
    res_verify = client.get("/api/words")
    words = [w["word"] for w in res_verify.json()]
    assert "pytest" not in words

def test_exact_search_trie(client):
    response = client.get("/api/search?q=computer")
    assert response.status_code == 200
    assert response.json()["word"] == "computer"

    response_404 = client.get("/api/search?q=nonexistentword")
    assert response_404.status_code == 404

def test_autocomplete_suggestions(client):
    response = client.get("/api/suggestions?q=com")
    assert response.status_code == 200
    suggestions = response.json()
    assert isinstance(suggestions, list)
    assert "computer" in suggestions

def test_fuzzy_search_typo(client):
    response = client.get("/api/search/fuzzy?q=computr")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["word"] == "computer"
    assert results[0]["distance"] == 1
