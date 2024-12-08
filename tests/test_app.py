import uuid
from datetime import datetime

import pytest
from flask.testing import FlaskClient

from geoparser.annotator.app import app, get_session
from geoparser.constants import DEFAULT_SESSION_SETTINGS
from tests.utils import get_static_test_file


@pytest.fixture(scope="session")
def client():
    return app.test_client()


def test_get_session():
    gazetteer = "geonames"
    session = get_session(gazetteer)
    assert type(session) is dict
    # valid uuid (would raise Error if not)
    uuid.UUID(session["session_id"])
    # valid datetime strings
    for date_field in ["created_at", "last_updated"]:
        assert datetime.fromisoformat(session[date_field])
    # gazetteer is the one specified
    assert session["gazetteer"] == gazetteer
    # default settings are applied initially
    assert session["settings"] == DEFAULT_SESSION_SETTINGS
    # documents are empty list
    assert type(session["documents"]) is list
    assert len(session["documents"]) == 0


def test_index(client: FlaskClient):
    response = client.get("/")
    # no errors: returns index html template
    assert b"<title>Geoparser Annotator</title>" in response.data


def test_start_new_session_get(client: FlaskClient):
    response = client.get("/start_new_session")
    # no errors: returns start_new_session html template
    assert b"<title>Start New Session</title>" in response.data


def test_start_new_session_post(client: FlaskClient):
    filename = "annotator_doc0.txt"
    response = client.post(
        "/start_new_session",
        data={
            "gazetteer": "geonames",
            "spacy_model": "en_core_web_sm",
            "files[]": [(open(get_static_test_file(filename), "rb"), filename)],
        },
        content_type="multipart/form-data",
    )
    # redirected to annotate page for first document
    assert b"/annotate/" in response.data
    assert b"?doc_index=0" in response.data
    assert True is False
