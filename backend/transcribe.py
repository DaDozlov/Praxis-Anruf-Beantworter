import logging
import time
import whisper
import warnings

# Filter torch weights_only warning
warnings.filterwarnings(
    "ignore",
    message="You are using `torch.load` with `weights_only=False`.*",
    category=FutureWarning,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function to transcribe audio file
def transcribe_audio(audio_file: str, model_size: str, retry_model: str):
    '''
    Function to transcribe an audio file using the Whisper model.
    
    Parameters:
        audio_file (str): The path to the audio file to be transcribed
        model_size (str): The size of the primary Whisper model to be used
        retry_model (str): The size of the fallback Whisper model to be used if the primary model fails
        
    Returns:
        result (dict): A dictionary containing the transcription result, duration, model used, success status, and error message
    '''
    result = { # initialize dictionary
        "transcription": None,
        "dauer": None,
        "model_used": model_size,
        "success": False,
        "error": None,
    }

    try:
        logging.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)  # use primary model

        start_time = time.time()  # start tracking time for transcription
        logging.info(f"Starting transcription for file: {audio_file}")
        transcription_result = model.transcribe(
            audio_file, language="de", fp16=False
        )  # specify language
        end_time = time.time()

        result.update(
            {  # update dictionary
                "transcription": transcription_result["text"],
                "dauer": end_time - start_time,
                "success": True,
            }
        )
        logging.info(
            f"Transcription successful. Duration: {result['dauer']:.2f} seconds."
        )

    except Exception as e:
        logging.error(f"Transcription failed with model '{model_size}': {e}")
        result["error"] = str(e)  # write error message into dictionary

        if retry_model:
            logging.info(f"Retrying transcription with fallback model: {retry_model}")
            try:
                model = whisper.load_model(retry_model)  # now use the backup model
                start_time = time.time()
                transcription_result = model.transcribe(
                    audio_file, language="de", fp16=False
                )
                end_time = time.time()

                result.update(
                    {
                        "transcription": transcription_result["text"],
                        "dauer": end_time - start_time,
                        "model_used": retry_model,
                        "success": True,
                        "error": None,  # reset error message when successful
                    }
                )
                logging.info(
                    f"Fallback transcription successful. Duration: {result['dauer']:.2f} seconds."
                )
            except Exception as retry_error:
                logging.error(
                    f"Retry transcription failed with model '{retry_model}': {retry_error}"
                )
                result["error"] = str(retry_error)

    return result
