import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Load your API key from an environment variable or a secure config
api_key = os.getenv("OPENAI_API_KEY")

def run_whisper(audio_path):
    """
    Transcribes audio using OpenAI Whisper API.

    Args:
        audio_path (str): Path to the audio file (.wav or other supported).

    Returns:
        str: Transcribed text from the audio.
    """
    client = openai.OpenAI(api_key=api_key)

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )

    return transcript
