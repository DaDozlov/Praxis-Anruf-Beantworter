import database
import random
import datetime
from datetime import timedelta
from app import app

subject = ("Überweisung", "Rezept")
satus = ("bearbeitet", "unbearbeitet")
vorname = (
    "Schneider",
    "Müller",
    "Schmidt",
    "Anderson",
    "Becker",
    "Mustermann",
    "Schweider",
    "Obenauf",
    "Horn",
)
nachname = (
    "Alexander",
    "Daniel",
    "Jonas",
    "Holga",
    "Robert",
    "Leon",
    "Elisabeth",
    "Monika",
    "Ida",
    "Maria",
)
nameMedikament = ("Ibuprophen", "Insulin", "Pennadeln", "Viviane Disk", "Zäpfchen")
fachrichtung = ("Orthopäde", "HNO", "Diabetologe", "Chirurg", "Dermatologe", "Urologe")
transkript = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."


def generate_phone_number():
    country_code = "+49"
    area_code = random.randint(100, 999)
    number = random.randint(1000000, 9999999)
    return f"{country_code} {area_code} {number}"


def generateBirthdate():
    day = str(random.randint(1, 28)).zfill(2)
    month = str(random.randint(1, 12)).zfill(2)
    year = random.randint(1970, 2000)
    return str(datetime.date(year, int(month), int(day)))


with app.app_context():
    for id in range(1, 40):
        anfragetyp = random.choice(subject)

        database.save_email_by_parameters(
            id=id,
            absender="none",
            subject="subject",
            status="unbearbeitet",
            empfangsdatum=datetime.datetime.now()
            + timedelta(hours=random.randint(1, 10), minutes=random.randint(1, 60)),
            anfragetyp=anfragetyp,
            fileName="audioName",
            dauer=1.0,
            vorname=random.choice(vorname),
            nachname=random.choice(nachname),
            geburtsdatum=generateBirthdate(),
            extraInformation="None",
            nameMedikament=random.choice(nameMedikament)
            if anfragetyp == "Rezept"
            else "None",
            dosis="60 mg" if anfragetyp == "Rezept" else "None",
            fachrichtung=random.choice(fachrichtung)
            if anfragetyp == "Überweisung"
            else "None",
            rating=0,
            grundUeberweisung="None",
            telefonnummer=generate_phone_number(),
            transkript=transkript,
        )
