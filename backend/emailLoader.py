import poplib
import email
import os
from dotenv import load_dotenv

from database import Email
from datetime import datetime

load_dotenv(dotenv_path="LogInData.env")

config = {
    "MAIL_SERVER": os.getenv("MAIL_SERVER"),
    "PORT": os.getenv("PORT"),
    "USER_MAIL": os.getenv("USER_MAIL"),
    "PASSWORD": os.getenv("PASSWORD"),
}


class MailLoader:
    """
    The Class responsible for the Connection and download of Emails from the Email Account which receives the answering machine audiofiles.
    It's necessary to set the mail_server, port, the email-adress and the Passwort in the "/tmp/LogInData.env" file to allow the Programm to work as intended.
    """

    def __init__(self):
        self.savedir = "tmp/"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not all(config.values()):
            raise ValueError("Missing required mail configuration in LogInData.env")
        self.connection = poplib.POP3_SSL(config["MAIL_SERVER"], int(config["PORT"]))
        self.connection.user(config["USER_MAIL"])
        self.connection.pass_(config["PASSWORD"])

    def load_emails(self):
        """
        Loads the emails from the Email Account specified in the "/tmp/LogInData.env" file.
        It's necessary to set the mail_server, port, the email-adress and the Passwort to allow the Programm to work as intended.
        The Actual loading is done via the POP3 protocoll by the poplib libarary. This allows the connection and returns a bitstream with all the relevant Emails in that account.

        Parameters:
            self: The class MailLoader which gives the function the necessary Log In Data. This has to be set manually once at the first initial setup in the aforementioned "/tmp/LogInData.env" file.

        Returns:
            emailList: A list of the Email Objects which make up the SQL-Alchemy Database. At this point only the ID, date_received, subject, sender and the filename of the audio get saved. Other Information gets processed by the LLM_Manager.


        """
        emails, total_bytes = self.connection.stat()
        print("{0} emails in the inbox, {1} bytes total".format(emails, total_bytes))
        emailList = []

        for i in range(emails):
            response = self.connection.retr(i + 1)
            raw_message = response[1]
            str_message = email.message_from_bytes(b"\n".join(raw_message))

            idraw = str_message["Message-ID"]
            emailId = idraw.split("<", 1)[1].split(">")[0]
            senderraw = str_message["From"]
            # TODO NUR WENN HIER AUCH < contains
            absender = senderraw
            if "<" in senderraw:
                absender = senderraw.split("<", 1)[1].split(">")[0]
            dateraw = str_message["Date"]
            try:
                dateraw = dateraw.replace(" (PST)", "")
            except ValueError as ve:
                print(ve)
            try:
                print(dateraw)
                date = datetime.strptime(dateraw, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError as ve:
                print(f"Date parsing error for email ID {emailId}: {ve}")
                continue
            subject = str_message["Subject"]
            audioName = ""

            # Saving the audiofile
            for part in str_message.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                fileName = part.get_filename()
                phonenumber = "0"
                try:
                    phonenumber = fileName.split("-")[0]
                except:
                    print("Keine Telefonnummer")

                if not fileName:
                    continue  # skip if no filename is found

                # rename the file to "audio_<email_id>.mp3"
                new_file_name = f"audio_{emailId}.mp3"
                audio_path = os.path.join(self.savedir, new_file_name)

                with open(audio_path, "wb") as fp:
                    print(f"Saving audio file: {new_file_name}")
                    fp.write(part.get_payload(decode=1))

                audioName = new_file_name  # update the audioName with the renamed file

            # Creation of Email Object with already known Data and saving in return list

            # TODO: uncomment and type your subject / absender
            # if subject != "type your subject" or absender != "your absender":
            #     continue

            mail = Email(
                id=emailId,
                absender=absender,
                subject=subject,
                status="unbearbeitet",
                empfangsdatum=date,
                anfragetyp="None",
                fileName=audioName,
                dauer=1.0,
                vorname="None",
                nachname="None",
                geburtsdatum="None",
                extraInformation="None",
                nameMedikament="None",
                dosis="None",
                fachrichtung="None",
                grundUeberweisung="None",
                telefonnummer=phonenumber,
                transkript="None",
                rating=0,
            )
            emailList.append(mail)

        self.connection.quit()
        return emailList
