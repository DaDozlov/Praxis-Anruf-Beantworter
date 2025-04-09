import datetime
import pytest
import glob
import os, shutil
from backend.app import return_app, set_database
from backend.database import Email



@pytest.fixture()
def app():
    app = return_app()
    return app


@pytest.fixture()
def database():
    db = set_database()
    
    return db


@pytest.fixture()
def db_setup(database, app):
    db = database
    email = Email(
        id="1",
        absender="Dieter Müller",
        subject="subject",
        status="bearbeitet",
        empfangsdatum=datetime.datetime.now(),
        anfragetyp="Überweisung",
        fileName="audio_test.mp3",
        dauer=1.0,
        vorname="Josef",
        nachname="Müller",
        geburtsdatum=datetime.datetime.now(),
        extraInformation="None",
        nameMedikament="None",
        dosis="None",
        fachrichtung="Neurologe",
        grundUeberweisung="Migräne",
        telefonnummer="+491773311131",
        transkript="transkript 1",
        rating=0,
    )
    with app.app_context():
        db.session.add(email)
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Email).filter(Email.id == "1").delete()
        db.session.commit()

@pytest.fixture()
def db_setup_two(database, app):
    db = database
    email = Email(
        id="1",
        absender="Dieter Müller",
        subject="subject",
        status="bearbeitet",
        empfangsdatum=datetime.datetime.now(),
        anfragetyp="Überweisung",
        fileName="audio_test.mp3",
        dauer=1.0,
        vorname="Josef",
        nachname="Müller",
        geburtsdatum=datetime.datetime.now(),
        extraInformation="None",
        nameMedikament="None",
        dosis="None",
        fachrichtung="Neurologe",
        grundUeberweisung="Migräne",
        telefonnummer="+491773311131",
        transkript="transkript 1",
        rating=0,
    )
    email2 = Email(
        id="2",
        absender="Luise@gmail.com",
        subject="subject",
        status="bearbeitet",
        empfangsdatum=datetime.datetime.now(),
        anfragetyp="Überweisung",
        fileName="audio_test.mp3",
        dauer=1.0,
        vorname="Dirk",
        nachname="Möller",
        geburtsdatum=datetime.datetime.now(),
        extraInformation="None",
        nameMedikament="None",
        dosis="None",
        fachrichtung="Nephrologe",
        grundUeberweisung="Migräne",
        telefonnummer="+491734211131",
        transkript="transkript 2",
        rating=0,
    )
    with app.app_context():
        db.session.add(email)
        db.session.add(email2)
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Email).filter(Email.id == "1").delete()
        db.session.query(Email).filter(Email.id == "2").delete()
        db.session.commit()


@pytest.fixture()
def email_cleanup(app, database):
    db = database
    yield
    with app.app_context():
        # Clean the database from the inserted mail
        db.session.query(Email).delete()
        db.session.commit()
    # Delete the downloaded audio files
    folder = 'tmp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                if "audio_test.mp3" not in file_path and "test.mp3" not in file_path :
                    os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


@pytest.fixture()
def client(app):
    return app.test_client()


def pytest_sessionfinish():
    """Hook to suppress logging errors after the session finishes."""
    import logging

    logging.raiseExceptions = False


