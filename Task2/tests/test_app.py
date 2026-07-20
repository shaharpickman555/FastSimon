import pytest

from main import create_app
from store import Database, MemoryStorage


@pytest.fixture
def client():
    app = create_app(Database(MemoryStorage()))
    app.config.update(TESTING=True)
    return app.test_client()


def body(response):
    return response.get_data(as_text=True).strip()


def test_index_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Task 2 Database" in response.data
    assert b"/static/app.js" in response.data


def test_sequence_1(client):
    assert body(client.get("/set?name=ex&value=10")) == "ex = 10"
    assert body(client.get("/get?name=ex")) == "10"
    assert body(client.get("/unset?name=ex")) == "ex = None"
    assert body(client.get("/get?name=ex")) == "None"
    assert body(client.get("/end")) == "CLEANED"


def test_sequence_2(client):
    assert body(client.get("/set?name=a&value=10")) == "a = 10"
    assert body(client.get("/set?name=b&value=10")) == "b = 10"
    assert body(client.get("/numequalto?value=10")) == "2"
    assert body(client.get("/numequalto?value=20")) == "0"
    assert body(client.get("/set?name=b&value=30")) == "b = 30"
    assert body(client.get("/numequalto?value=10")) == "1"
    assert body(client.get("/end")) == "CLEANED"


def test_sequence_3(client):
    assert body(client.get("/set?name=a&value=10")) == "a = 10"
    assert body(client.get("/set?name=b&value=20")) == "b = 20"
    assert body(client.get("/get?name=a")) == "10"
    assert body(client.get("/get?name=b")) == "20"
    assert body(client.get("/undo")) == "b = None"
    assert body(client.get("/get?name=a")) == "10"
    assert body(client.get("/get?name=b")) == "None"
    assert body(client.get("/set?name=a&value=40")) == "a = 40"
    assert body(client.get("/get?name=a")) == "40"
    assert body(client.get("/undo")) == "a = 10"
    assert body(client.get("/get?name=a")) == "10"
    assert body(client.get("/undo")) == "a = None"
    assert body(client.get("/get?name=a")) == "None"
    assert body(client.get("/undo")) == "NO COMMANDS"
    assert body(client.get("/redo")) == "a = 10"
    assert body(client.get("/redo")) == "a = 40"
    assert body(client.get("/end")) == "CLEANED"


def test_redo_is_cleared_after_new_command(client):
    assert body(client.get("/set?name=x&value=1")) == "x = 1"
    assert body(client.get("/undo")) == "x = None"
    assert body(client.get("/set?name=y&value=2")) == "y = 2"
    assert body(client.get("/redo")) == "NO COMMANDS"


def test_bad_inputs_are_graceful(client):
    response = client.get("/set?name=a")
    assert response.status_code == 400
    assert body(response) == "ERROR: missing or invalid 'value'"

    response = client.get("/get?name=bad%20name")
    assert response.status_code == 400
    assert body(response) == "ERROR: missing or invalid 'name'"
