from email import message
import re
import time
from .emailSender import send_mail
import ast
import pytest
from backend.database import Email

# Test for standard page
def test_home(client):
    response = client.get("/")
    assert b"<p>Backend page.</p>" in response.data


# Test for Mail loading working as intended, functionality confirmed in test_all
def test_email(client):
    response = client.get("/email")
    assert b"success" in response.data


# Test for getting a transcript corresponding to the id
def test_transkript_1(client, db_setup):
    response = client.post("/transkript", query_string={"id": "1"})
    assert b"transkript 1" in response.data
# Same as before but with two rows in the database
def test_transkript_2(client, db_setup_two):
    response = client.post("/transkript", query_string={"id": "2"})
    assert b"transkript 2" in response.data
def test_transkript_3(client, db_setup_two):
    response = client.post("/transkript", query_string={"id": "1"})
    assert not b"transkript 2" in response.data


# Test for confirming the download of a send email; sends one email with a random subject which then gets checked if downloaded to the database
def test_all(client, email_cleanup):
    subject = send_mail()
    client.get("/email")
    response = client.get("/all")

    list = ast.literal_eval(response.data.decode('utf-8'))
    foundSubject = False
    for x in list:
        if x["subject"] == subject:
            foundSubject = True
            break
    email_cleanup
    assert foundSubject

# Test for confirming the download of a send email; sends 2 emails with random subjects which then get checked if downloaded to the database
def test_all_2(client,email_cleanup):
    subject1 = send_mail()
    subject2 = send_mail()
    client.get("/email")
    response = client.get("/all")

    list = ast.literal_eval(response.data.decode('utf-8'))
    foundSubject1 = False
    foundSubject2 = False
    for x in list:
        if x["subject"] == subject1:
            foundSubject1 = True
        if x["subject"] == subject2:
            foundSubject2 = True
    email_cleanup
    assert foundSubject1 and foundSubject2

# Update the vorname of a row
def test_update(app, client, db_setup, database):
    response = client.post("/update", query_string={"id": "1", "column": "vorname", "value": "Heinrich"})
    db = database
    with app.app_context():
        assert db.session.query(Email).filter(Email.id == "1").first().vorname == "Heinrich"
# User gives a rating to an email
def test_update_2(app, client, db_setup, database):
    response = client.post("/update", query_string={"id": "1", "column": "rating", "value": "5"})
    db = database
    with app.app_context():
        assert db.session.query(Email).filter(Email.id == "1").first().rating == 5

# Delete the requested email
def test_delete(app, client, db_setup, database):
    response = client.post("/delete", query_string={"id": "1"})
    db = database
    with app.app_context():
        assert db.session.query(Email).filter(Email.id == "1").first() is None
# Delete the requested email while not deleting another one which is also in the database
def test_delete_2(app, client, db_setup_two, database):
    response = client.post("/delete", query_string={"id": "1"})
    db = database
    with app.app_context():
        assert db.session.query(Email).filter(Email.id == "1").first() is None and db.session.query(Email).filter(Email.id == "2").first() is not None



def test_audio(client, db_setup):
    # give id and compare to audio
    response = client.post("/audio", query_string={"fileName": "test"})
    disposition = response.headers.getlist("Content-Disposition")

    assert disposition is not None    
    
    if disposition is not None:
        filename = disposition[0].split("filename=")[1]
    
    assert filename == "audio_test.mp3"


def test_whisper_modell(client):
    response = client.post("/set-whisper-model", query_string={"model": "large"})
    message = response.data.decode("utf-8")

    assert "Set whisper model to large" in message


def test_whisper_modell_2(client):
    response = client.post("/set-whisper-model", query_string={"model": ""})
    message = response.data.decode("utf-8")

    assert "error" in message


def test_reprocess(client, db_setup):
    response = client.post("/reprocess", query_string={"id": "1"})
    message = response.data.decode("utf-8")

    assert "Die Wiederaufbereitung wurde gestartet" in message


def test_reprocess_2(client, db_setup):
    response = client.post("/reprocess", query_string={"id": "3"})
    message = response.data.decode("utf-8")

    assert "error" in message
    
    
def test_debug(app, client, db_setup):
    response = client.get("/all")
    
    upload = app.config["UPLOAD_FOLDER"]
    database = app.config["SQLALCHEMY_DATABASE_URI"]
    
    print(f"\n\nRunning with Configuration:\n\n{upload}\n{database}\n")
    
    message = response.data.decode("utf-8")
    
    print(message)
    
    assert response.status_code == 200
