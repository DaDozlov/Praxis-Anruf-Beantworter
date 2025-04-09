import subprocess
import logging
import json


def run_llm(transcription: str):
    """
    Run the LLM model using Ollama to extract structured information from a given transcription.

    This function interacts with a locally running LLM (e.g., Mistral) using the `ollama` command-line interface.
    It sends a prompt formatted to extract specific information from the transcription and expects the response in JSON format.

    Parameters:
    ----------
    transcription : str
        The transcription text from which structured information needs to be extracted.
        This is typically a voicemail transcription or similar free-text input.

    Returns:
    -------
    dict or None
        If successful, returns a dictionary containing the extracted data with keys:
        - "vorname": First name of the individual.
        - "nachname": Last name of the individual.
        - "anfragetyp": Type of request ("Rezept" or "Überweisung").
        - "nameMedikament": Name of the medication (if applicable).
        - "dosis": Dosage of the medication (if applicable).
        - "fachrichtung": Specialty field (if applicable).
        - "grundUeberweisung": Reason for referral (if applicable).
        - "extraInformation": Any additional information extracted.
        - "geburtsdatum": Date of birth.

        Returns `None` if an error occurs (e.g., JSON parsing fails, the subprocess encounters an error, or the command times out).
    """
    try:
        formatted_prompt = (
            f"Extrahieren Sie die Informationen aus der Transkription und geben Sie nur ein JSON-Objekt im folgenden Format zurück:\n\n"
            '{ "vorname": ..., "nachname": ..., "anfragetyp": ..., "nameMedikament": ..., "dosis": ..., "fachrichtung": ..., "grundUeberweisung": ..., "extraInformation": ..., "geburtsdatum":...}\n\n'
            "'anfragetyp' kann nur 'Rezept' oder 'Überweisung' sein. Geben Sie nur das JSON-Objekt zurück."
            f'Transkription: "{transcription}"\n\n'
        )

        logging.debug(f"Running LLM with prompt: {formatted_prompt}")

        # TODO: fix, return back LLM or tinyllama
        cmd = ["ollama", "run", "mistral"]
        result = subprocess.run(
            cmd,
            input=formatted_prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=360,
        )

        logging.debug(f"LLM stdout: {result.stdout}")
        logging.debug(f"LLM stderr: {result.stderr}")

        if result.returncode != 0:
            logging.error(f"LLM returned an error: {result.stderr}")
            return None

        output = result.stdout.strip()

        # attempt to parse the JSON output
        try:
            extracted_data = json.loads(output)
            logging.debug(f"Extracted data: {extracted_data}")
            return extracted_data
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON output: {e}")
            return None

    except subprocess.TimeoutExpired:
        logging.error("LLM command timed out")
        return None
    except Exception as e:
        logging.error(f"An error occurred while running LLM: {str(e)}")
        return None
