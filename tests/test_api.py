"""API tests. They need a PostgreSQL database: set DATABASE_URL (the tables are wiped between tests,
so point it at a test database). In CI, the workflow starts one; locally, `docker compose up -d db` works."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # the app serves static files and templates by relative path
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.pop("OPENAI_API_KEY", None)

if not os.getenv("DATABASE_URL"):
    pytest.skip("DATABASE_URL is not set: these tests need a PostgreSQL database", allow_module_level=True)

import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client():
    main.db.reset()  # start every test with empty tables
    return TestClient(main.app)


ALICE, BOB = "090000045", "094019245"  # valid test AFMs (correct check digit)

RETURN = dict(name="Alice", address="Odos 1, Athens", family_status="single", children=0,
              salary=30000, freelance=0, rental=0, investments=0, business=0, medical=0, donations=0,
              insurance=0, renovation=0, property_details="-", property_value=0, vehicles="-",
              tax_prepayments=0, insurance_payments=0)


def signup(client, afm, password="password123"):
    response = client.post("/signup", json={"afm": afm, "email": f"{afm}@example.com", "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_signup_and_login(client):
    signup(client, ALICE)
    response = client.post("/token", data={"username": ALICE, "password": "password123"})
    assert response.status_code == 200
    assert client.post("/token", data={"username": ALICE, "password": "wrong-password"}).status_code == 400


def test_signup_rejects_bad_input(client):
    bad = [
        {"afm": "123456789", "email": "a@example.com", "password": "password123"},  # wrong check digit
        {"afm": "000000000", "email": "a@example.com", "password": "password123"},
        {"afm": ALICE, "email": "not-an-email", "password": "password123"},
        {"afm": ALICE, "email": "a@example.com", "password": "short"},
    ]
    for body in bad:
        assert client.post("/signup", json=body).status_code == 422, body


def test_duplicate_signup(client):
    signup(client, ALICE)
    response = client.post("/signup", json={"afm": ALICE, "email": "x@example.com", "password": "password123"})
    assert response.status_code == 400


def test_submit_and_read_back(client):
    headers = signup(client, ALICE)
    assert client.post("/submit", json=dict(RETURN, afm=ALICE), headers=headers).status_code == 200
    data = client.get("/get_tax_submissions", headers=headers).json()
    assert data["person_info"]["name"] == "Alice"
    assert len(data["tax_details_info"]) == 1


def test_cannot_submit_for_another_user(client):
    alice = signup(client, ALICE)
    bob = signup(client, BOB)
    client.post("/submit", json=dict(RETURN, afm=ALICE), headers=alice)

    response = client.post("/submit", json=dict(RETURN, name="Mallory", afm=ALICE), headers=bob)
    assert response.status_code == 403

    data = client.get("/get_tax_submissions", headers=alice).json()
    assert data["person_info"]["name"] == "Alice"
    assert len(data["tax_details_info"]) == 1


def test_submit_validates_input(client):
    headers = signup(client, ALICE)
    assert client.post("/submit", json=dict(RETURN, afm="abc"), headers=headers).status_code == 422
    assert client.post("/submit", json=dict(RETURN, afm=ALICE, salary=-5), headers=headers).status_code == 422


def test_endpoints_require_login(client):
    assert client.get("/get_tax_submissions").status_code == 401
    assert client.post("/submit", json=dict(RETURN, afm=ALICE)).status_code == 401
    assert client.post("/generate_advice", json={"uid": "x"}).status_code == 401


def test_new_user_has_no_submissions(client):
    headers = signup(client, ALICE)
    data = client.get("/get_tax_submissions", headers=headers).json()
    assert data == {"person_info": None, "tax_details_info": []}


def test_advice_only_for_own_submissions(client):
    alice = signup(client, ALICE)
    bob = signup(client, BOB)
    uid = client.post("/submit", json=dict(RETURN, afm=ALICE), headers=alice).json()["uid"]
    assert client.post("/generate_advice", json={"uid": uid}, headers=bob).status_code == 404
    # Without an OpenAI key the feature reports that it is unavailable instead of crashing
    assert client.post("/generate_advice", json={"uid": uid}, headers=alice).status_code == 503


def test_advice_prompt_contains_no_personal_details():
    prompt = main.build_advice_prompt(dict(RETURN, afm=ALICE, uid="u", submission_date="d"))
    assert ALICE not in prompt and "Alice" not in prompt and "Odos" not in prompt
    assert "30000" in prompt


def test_pages_load(client):
    for path in ["/", "/tables", "/login-page", "/signup-page"]:
        assert client.get(path).status_code == 200
