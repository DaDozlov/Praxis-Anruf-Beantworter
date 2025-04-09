import logging
import os
from llm import run_llm
from transcribe import transcribe_audio
import threading
from database import Email, db
import os
from dotenv import load_dotenv


# Class to manage the LLM and audio processing
class LLM_Manager:
    """Class to manage the LLM and audio processing."""

    # Initialize the LLM Manager with the Flask app
    def __init__(self, app):
        """Initialize the LLM Manager with the Flask app."""
        load_dotenv(dotenv_path="LogInData.env")
        config = {"LLM": os.getenv("LLM")}
        self.app = app
        self.selected_llm = config["LLM"]
        self.timeout = 180
        self.primary_transcription_model = "small"
        self.fallback_transcription_model = "tiny"

    # Function to set the LLM
    def set_llm(self, llm_name: str):
        """Function to set the LLM."""
        if llm_name in ["llama2", "mistral"]:
            self.selected_llm = llm_name
            logging.info(f"LLM set to {llm_name}")
        else:
            raise ValueError("Invalid LLM selected.")

    # Function to set the timeout
    def set_timeout(self, timeout: int):
        """Function to set the timeout."""
        self.timeout = timeout
        logging.info(f"Timeout set to {timeout} seconds.")

    def get_transcription_model(self):
        """
        Get the currently selected primary transcription model.
        Returns:
            str: The name of the primary transcription model.
        """
        return self.primary_transcription_model

    # Function to set the transcription models
    def set_transcription_models(self, primary_model: str, fallback_model: str):  #
        self.primary_transcription_model = primary_model
        self.fallback_transcription_model = fallback_model
        logging.info(
            f"Primary transcription model: {primary_model}, Fallback model: {fallback_model}"
        )

    # Function to transcribe the audio
    def transcribe_audio(self, audio_file_path: str):
        """
        Transcribe audio using the configured transcription models.

        Parameters:
        ----------
        audio_file_path : str
            Path to the audio file.

        Returns:
        -------
        dict or None
            Transcription result dictionary or None if transcription fails.
        """

        logging.info(f"Transcribing audio file: {audio_file_path}")
        logging.info(f"Using Whisper model: {self.primary_transcription_model}")
        result = transcribe_audio(
            audio_file_path,
            self.primary_transcription_model,
            self.fallback_transcription_model,
        )
        if not result["success"]:
            logging.error(f"Transcription failed: {result['error']}")
            return None
        logging.info(f"Transcription completed: {result['transcription']}")
        return result

    # Function to extract information
    def extract_information(self, transcription: str):
        """
        Extract structured information from transcription text.

        Parameters:
        ----------
        transcription : str
            Transcription text for information extraction.

        Returns:
        -------
        dict or None
            Extracted data dictionary or None if extraction fails.
        """
        if self.selected_llm == "llama2":
            return run_llm(transcription)
        else:
            raise RuntimeError("No valid LLM selected.")

    # Function to process the audio
    def process_audio(self, audio_file_path: str):
        """
        Process audio by transcribing and extracting information.

        Parameters:
        ----------
        audio_file_path : str
            Path to the audio file.

        Returns:
        -------
        dict or None
            Dictionary containing transcription and extracted information or None if processing fails.
        """

        transcription_result = self.transcribe_audio(audio_file_path)
        if not transcription_result:
            logging.error("Transcription failed.")
            return None

        transcription_text = transcription_result["transcription"]

        extracted_data = self.extract_information(transcription_text)
        if not extracted_data:
            logging.error("Information extraction failed.")
            return None

        email_data = {
            "transcription": transcription_text,
            "data": extracted_data,
            "model_used": transcription_result.get("model_used", "unknown"),
            "dauer": transcription_result.get("dauer", 0),
        }

        return email_data

    # Function to process the email
    def process_email(self, email):
        """
        Process an email, including transcription and information extraction.

        Parameters:
        ----------
        email : Email
            Email object from the database to process.
        """

        def run():
            """Function to run the processing in a new thread."""
            with self.app.app_context():
                try:
                    email_in_thread = Email.query.filter_by(id=email.id).first()
                    if email_in_thread is None:
                        logging.error(f"Email {email.id} not found in the database.")
                        return

                    email_in_thread.status = "abfertigung"
                    db.session.commit()

                    audio_file_path = os.path.join(
                        self.app.config["UPLOAD_FOLDER"], email_in_thread.fileName
                    )
                    transcription_result = self.transcribe_audio(audio_file_path)
                    if not transcription_result:
                        logging.error("Transcription failed.")
                        email_in_thread.status = "fehlgeschlagen"
                        db.session.commit()
                        return

                    transcription_text = transcription_result["transcription"]
                    email_in_thread.transkript = (
                        transcription_text  # save the transcription
                    )

                    logging.info("Starting information extraction with Llama2.")
                    extracted_data = run_llm(transcription_text)
                    if extracted_data is None:
                        logging.error("Information extraction failed.")
                        email_in_thread.status = "fehlgeschlagen"
                        db.session.commit()
                        return

                    logging.info("Information extraction completed.")
                    logging.info(f"LLM output: {extracted_data}")

                    # Update the email with the extracted data
                    for key in [
                        "vorname",
                        "nachname",
                        "anfragetyp",
                        "nameMedikament",
                        "dosis",
                        "fachrichtung",
                        "grundUeberweisung",
                        "extraInformation",
                        "geburtsdatum",
                    ]:
                        value = extracted_data.get(key)
                        if hasattr(email_in_thread, key):
                            setattr(email_in_thread, key, value or None)
                        else:
                            logging.warning(
                                f"Attribute {key} does not exist on Email model."
                            )

                    # Update status to "unbearbeitet"
                    email_in_thread.status = "unbearbeitet"
                    # Update rating to 0
                    email_in_thread.rating = 0
                    db.session.commit()
                    logging.info(f"Email {email_in_thread.id} bearbeitet successfully.")

                except Exception as e:
                    logging.error(f"Error processing email {email.id}: {e}")
                    # Ensure email status is updated in case of exceptions
                    email_in_thread = Email.query.filter_by(id=email.id).first()
                    if email_in_thread:
                        email_in_thread.status = "fehlgeschlagen"
                        db.session.commit()

        # start the processing in a new thread
        thread = threading.Thread(target=run)
        thread.start()
