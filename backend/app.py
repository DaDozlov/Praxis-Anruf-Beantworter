import logging
from flask import Flask, request, send_file
from flask_migrate import Migrate
from llm_manager import LLM_Manager
import os
from database import db
from database import (
    init_db,
    get_all_emails,
    save_email,
    Email,
    delete,
    update_column,
    transkript,
)
from flask import jsonify
from flask_cors import CORS
from emailLoader import MailLoader
import atexit
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

last_scheduler_run_time = None

app = Flask(__name__)
app.debug = True
CORS(app)

app.config["UPLOAD_FOLDER"] = "tmp"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

init_db(app)
migrate = Migrate(app, db)

# singleton method
llm_manager = None


def set_database():
    app.config["UPLOAD_FOLDER"] = "../tests/tmp"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return db


Test = False


def return_app():
    Test = True
    return app


def create_llm_manager(app):
    global llm_manager
    if llm_manager is None:
        llm_manager = LLM_Manager(app)
        # Check if a transcription model is set; if not, set a default
        if not llm_manager.get_transcription_model():
            default_model = "tiny"  # Default Whisper model
            llm_manager.set_transcription_models(default_model, "tiny")
            logging.info(f"Default Whisper model initialized to: {default_model}")
    return llm_manager


llm_manager = create_llm_manager(app)


def emailCheck():
    """Checks for new Emails using the MailLoader class in regular Intervalls (30s Standard) by using the Backgroundscheduler"""
    global last_scheduler_run_time
    with app.app_context():
        emailLoader = MailLoader()
        emails = emailLoader.load_emails()
        for mail in emails:
            existing_email = Email.query.filter_by(id=mail.id).first()
            if not existing_email:
                mail.status = "processed"
                save_email(mail)
            else:
                logging.info(f"Email {mail.id} already exists. Skipping.")
        last_scheduler_run_time = datetime.datetime.now()
    with app.app_context():
        for mail in Email.query.filter_by(status="processed"):
            llm_manager.process_email(mail)


if not Test:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=emailCheck, trigger="interval", seconds=30)
    scheduler.start()
    # Shuts down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


@app.route("/")
def index():
    return "<p>Backend page.</p>"


# Manually load new mails from the email account specified in the LogInData.env
@app.route("/email")
def load_all_emails():
    """
    Loads all emails from the email account specified in the LogInData.env

    Parameters:
        None

    Returns:
        Message (json): "success" or the error which happened
    """
    emailLoader = MailLoader()
    emails = emailLoader.load_emails()
    for mail in emails:
        save_email(mail)
    return jsonify("success")


@app.route("/last-scheduler-run", methods=["GET"])
def get_last_scheduler_run():
    """Returns the last time the scheduler ran."""
    if last_scheduler_run_time:
        return jsonify({"last_run": last_scheduler_run_time.isoformat()}), 200
    return jsonify({"last_run": None}), 200


# Route to get all data from the database as an array with dictionaries
@app.route("/all")
def get_all_emails_route():
    """
    Returns all emails in the database

    Parameters:
        None

    Returns:
        emails (json): an array with dictionaries of all emails in the database
    """
    emails = get_all_emails()
    return jsonify(emails)


@app.route("/delete", methods=["POST"])
def delete_email():
    """
    Deletes the email with the specified id and removes the associated audio file.

    Parameters:
        id (str): The id which is the primary key in the database.

    Returns:
        Message (json): "success" or the error which happened.
    """
    if request.method == "POST":
        email_id = request.args.get("id")
        if not email_id:
            return jsonify({"error": "id is missing"}), 400

        email = Email.query.filter_by(id=email_id).first()
        if not email:
            logging.error(f"Email with ID {email_id} not found in the database.")
            return jsonify({"error": "Email not found"}), 404

        file_name = email.fileName

        if not file_name.startswith("audio_"):
            file_name = f"audio_{file_name}"

        if not file_name.endswith(".mp3"):
            file_name += ".mp3"

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)

        # delete the file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Successfully deleted audio file: {file_path}")
            except Exception as e:
                logging.error(f"Failed to delete audio file: {e}")
                return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
        else:
            logging.warning(f"File not found at path: {file_path}")

        # delete the email from the database
        delete(email_id)
        logging.info(f"Successfully deleted email entry from database: {email_id}")

        return jsonify({"message": "success"}), 200

    return jsonify({"error": "Invalid request method"}), 405


# Route to update a column of a row of Email
@app.route("/update", methods=["POST"])
def update():
    """
    Updates the specified column in the row with the specified id to the specified value

    Parameters:
        id (str): for identifying the row
        column (str): for identifying the column
        value (str/int/date/float/DateTime): the value which the specified column of the specified row has to change to

    Returns:
        Message (json): "message" : "Update successful" or the error which happened
    """
    if request.method == "POST":
        id = request.args.get("id")
        column = request.args.get("column")
        value = request.args.get("value")
        if not id or not column or value is None:
            return jsonify({"error": "id, column, or value is missing"}), 400
        try:
            update_column(id, column, value)
            return jsonify({"message": "Update successful"}), 200
        except Exception as e:
            logging.error(f"Update failed: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid request method"}), 405


@app.route("/audio", methods=["GET", "POST"])
def get_audio():
    """
    Returns the requested audio file

    Parameters:
        fileName (str): The filename in the database and Folder

    Returns:
        audioFile (send_file): Returns the file in the flask send_file format
    """
    fileName = request.args.get("fileName")
    fileName = f"audio_{fileName}"

    logging.info(f"{fileName}")

    if not fileName:
        logging.error("Missing fileName parameter")
        return jsonify({"error": "fileName is missing"}), 400

    try:
        # Append .mp3 if missing
        if not fileName.endswith(".mp3"):
            fileName += ".mp3"

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], fileName)
        logging.info(f"Looking for file at: {file_path}")

        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return jsonify({"error": f"File {fileName} not found"}), 404

        return send_file(file_path, mimetype="audio/mpeg")
    except Exception as e:
        logging.error(f"Error serving file: {e}")
        return jsonify({"error": f"Failed to serve file: {str(e)}"}), 500


# Route to get the transcript
@app.route("/transkript", methods=["POST"])
def get_transcript():
    """
    Returns the requested transcript

    Parameters:
        id (str): The id which is the primary key in the database

    Returns:
        transcript (str): Returns transcript associated with the id if there is a matching id
    """
    if request.method == "POST":
        id = request.args.get("id")
        if id is None:
            return jsonify({"error": "id is missing"}), 400
        try:
            return transkript(id)
        except Exception as e:
            logging.error(f"Couldn't find the transkript to the matching id: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid request method"}), 405


# Route to set the whisper model
@app.route("/set-whisper-model", methods=["POST"])
def set_whisper_model():
    """
    Sets the whisper model to the specified model

    Parameters:
        model (str): The model which the whisper model has to be set to

    Returns:
        Message (json): "message" : "Set whisper model to {model}" or the error which happened
    """
    model = request.args.get("model")
    if not model:
        return jsonify({"error": "No model parameter provided"}), 400

    try:
        llm_manager.set_transcription_models(model, "tiny")
        logging.info(f"Whisper model updated to: {model}")
        return jsonify({"message": f"Set whisper model to {model}."}), 200
    except Exception as e:
        logging.error(f"Failed to set Whisper model: {e}")
        return jsonify({"error": "Failed to set Whisper model"}), 500


@app.route("/get-whisper-model", methods=["GET"])
def get_whisper_model():
    """
    Returns the current Whisper transcription model.

    Returns:
        json: The current Whisper model being used.
    """
    try:
        current_model = llm_manager.get_transcription_model()
        return jsonify({"model": current_model}), 200
    except Exception as e:
        logging.error(f"Error fetching Whisper model: {e}")
        return jsonify({"error": "Could not fetch Whisper model"}), 500


# Route to set the reprocess audio file
@app.route("/reprocess", methods=["POST"])
def reprocess_audio():
    """
    Reprocesses the audio file with the specified id

    Parameters:
        id (str): The id which is the primary key in the database

    Returns:
        Message (json): "message" : "Reprocessing started" or the error which happened
    """
    email_id = request.args.get("id")
    if not email_id:
        return jsonify({"error": "Email ID nicht gefunden"}), 400

    email = Email.query.filter_by(id=email_id).first()
    if not email:
        return jsonify({"error": "Email nicht gefunden"}), 404

    audio_file_path = os.path.join(app.config["UPLOAD_FOLDER"], email.fileName)
    if not os.path.exists(audio_file_path):
        return jsonify({"error": "Audiodatei nicht gefunden"}), 404

    try:
        llm_manager.process_email(email)
        return jsonify({"message": "Die Wiederaufbereitung wurde gestartet."}), 200
    except Exception as e:
        email.status = "fehlgeschlagen"
        save_email(email)
        logging.error(f"Error Wiederaufbereitung Email {email_id}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("backend.log"), logging.StreamHandler()],
    )
    app.run(debug=True, use_reloader=False)
