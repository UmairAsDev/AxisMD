
import os
from openai import OpenAI

def transcribe_audio(file_path: str, api_key: str | None = None) -> str:
    """
    Transcribe a WAV/MP3/M4A file using OpenAI gpt-4o-mini-transcribe.
    Requires environment OPENAI_API_KEY or api_key param.
    Returns the plain text transcript.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing. Set it in your environment.")

    client = OpenAI(api_key=key)
    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model = "gpt-4o-mini-transcribe",
            file = f,
            response_format = "text",
            # Set additional parameters for best results
            # language="en",  # Specify language if known for better accuracy
            # prompt="This is a transcription of a voice recording.", # Provide context if available
            # temperature=0.0 # Lower temperature for more deterministic output
        )
    # SDK returns a plain text string when response_format="text"
    return response if isinstance(response, str) else getattr(response, "text", "")


