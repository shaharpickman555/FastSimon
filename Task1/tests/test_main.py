from main import app


def test_hello_world_page():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Hello World!" in response.data
    assert b"App Engine Standard Environment with Python 3." in response.data
