# Importing the Required Libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from smtplib import SMTP_SSL as SMTP       
from random import randrange

def send_mail():

    # Loading from file
    load_dotenv(dotenv_path="LogInTestData.env")
    configs = {
        "MAIL_SERVER": os.getenv("1MAIL_SERVER"),
        "PORT": os.getenv("1PORT"),
        "USER_MAIL": os.getenv("1USER_MAIL"),
        "PASSWORD": os.getenv("1PASSWORD"),
    }

    # Setting up the Email Details
    sender_email = configs["USER_MAIL"]
    receiver_email = configs["USER_MAIL"]
    subject = str(randrange(10000))
    body = "Dear Server,\n\nPlease find the attached document.\n\nBest regards,\nUnittest"

    # Creating the Email Object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attaching the File
    attachment_path = "tmp/test.mp3"
    print(os.path.isfile(attachment_path))

    # Attach the file using the MIMEBase class
    attachment = open(attachment_path, "rb")
    payload = MIMEBase("application", "octet-stream")
    payload.set_payload((attachment).read())
    encoders.encode_base64(payload)
    payload.add_header(
        "Content-Disposition", f"attachment; filename= {attachment_path.split('/')[-1]}"
    )
    message.attach(payload)

    # Establishing the SMTP Connection
    smtp_server = configs["MAIL_SERVER"]
    smtp_port = configs["PORT"]

    print("SICHER DAS DU HIER BIST?!??")
    print("Start email")
    print(smtp_server)
    print(smtp_port)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        print("Inside server")
        server.starttls()
        server.login(sender_email, configs["PASSWORD"])
        server.send_message(message)
        print("Send email success")
    return subject


if __name__ == "__main__":
    send_mail()
