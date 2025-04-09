import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Defines the Email Table Model with all their respective columns
class Email(db.Model):
    '''
    The Object which makes up the SQL-Alchemy Database.
    The necessary data columns are defined here.
    '''
    id = db.Column("id", db.String(120), primary_key=True)
    absender = db.Column("absender", db.String(120))
    subject = db.Column("subject", db.String(120))
    status = db.Column("status", db.String(120))
    empfangsdatum = db.Column("empfangsdatum", db.DateTime, default=datetime.utcnow)
    anfragetyp = db.Column("anfragetyp", db.String(120))
    fileName = db.Column("fileName", db.String(120))
    dauer = db.Column("dauer", db.Float)
    vorname = db.Column("vorname", db.String(120))
    nachname = db.Column("nachname", db.String(120))
    geburtsdatum = db.Column("geburtsdatum", db.String(120))
    extraInformation = db.Column("extraInformation", db.String(120))
    nameMedikament = db.Column("nameMedikament", db.String(120))
    dosis = db.Column("dosis", db.String(120))
    fachrichtung = db.Column("fachrichtung", db.String(120))
    grundUeberweisung = db.Column("grundUeberweisung", db.String(120))
    telefonnummer = db.Column("telefonnummer", db.String(20))
    transkript = db.Column("transkript", db.String(2096))
    rating = db.Column("rating", db.Integer)


# Initialize the database with the Flask app
def init_db(app):
    '''Initialize the database with the Flask app.'''
    db.init_app(app)
    with app.app_context():
        db.create_all()


# Function to save a new message to the database
def save_email_by_parameters(
    id,
    absender,
    subject,
    status,
    empfangsdatum,
    anfragetyp,
    fileName,
    dauer,
    vorname,
    nachname,
    geburtsdatum,
    extraInformation,
    nameMedikament,
    dosis,
    fachrichtung,
    grundUeberweisung,
    telefonnummer,
    transkript,
    rating,
):
    '''Function to save a new message to the database.'''
    email = Email(
        id=id,
        absender=absender,
        subject=subject,
        status=status,
        empfangsdatum=empfangsdatum,
        anfragetyp=anfragetyp,
        fileName=fileName,
        dauer=dauer,
        vorname=vorname,
        nachname=nachname,
        geburtsdatum=geburtsdatum,
        extraInformation=extraInformation,
        nameMedikament=nameMedikament,
        dosis=dosis,
        fachrichtung=fachrichtung,
        grundUeberweisung=grundUeberweisung,
        telefonnummer=telefonnummer,
        transkript=transkript,
        rating=rating,
    )
    db.session.add(email)
    db.session.commit()

# Function to save an email to the database
def save_email(email):
    '''Function to save an email to the database.'''
    try:
        db.session.add(email)
        db.session.commit()
        print("AAAALARM")
        logging.info(f"Email {email.id} saved to the database.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to save email {email.id}: {e}")


# Function to retrieve all messages
def get_all_emails():
    '''Function to retrieve all messages.'''
    emails = Email.query.all()
    return [
        {
            "id": email.id,
            "absender": email.absender,
            "subject": email.subject,
            "status": email.status,
            "empfangsdatum": email.empfangsdatum.strftime("%Y-%m-%d %H:%M:%S"),
            "anfragetyp": email.anfragetyp,
            "fileName": email.fileName,
            "dauer": email.dauer,
            "vorname": email.vorname,
            "nachname": email.nachname,
            "geburtsdatum": email.geburtsdatum,
            "extraInformation": email.extraInformation,
            "nameMedikament": email.nameMedikament,
            "dosis": email.dosis,
            "fachrichtung": email.fachrichtung,
            "grundUeberweisung": email.grundUeberweisung,
            "telefonnummer": email.telefonnummer,
            "transkript": email.transkript,
            "rating": email.rating,
        }
        for email in emails
    ]


# Function to get a specific message by fileName
def get_email_by_filename(fileName):
    '''Function to get a specific message by fileName.'''
    return Email.query.filter_by(fileName=fileName).first()


# Delete email by id
def delete(id):
    '''Delete email by id.'''
    Email.query.filter(Email.id == id).delete()
    db.session.commit()


# Get transkript from id
def transkript(id):
    '''Get transkript from id.'''
    return Email.query.filter(Email.id == id).first().transkript


# Update a column of an Email row specified by the id
def update_column(id, column, value):
    '''Update a column of an Email row specified by the id.'''
    Email.query.filter(Email.id == id).update({column: value})
    db.session.commit()


# Return unprocessed Mails to begin processing
def unprocessed_emails():
    '''Return unprocessed Mails to begin processing.'''
    return Email.query.filter_by(status="unbearbeitet")
