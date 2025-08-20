
import os
from dotenv import load_dotenv
load_dotenv()
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from audio_recorder import AudioRecorder
from stt import transcribe_audio
from save_notes import save_transcript

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def voice_agent():
    """
    Simple CLI voice agent:
    1) Records a short audio clip (press Enter to start/stop).
    2) Transcribes it using OpenAI gpt-4o-mini-transcribe.
    3) Prints and saves the transcript to notes/transcripts.jsonl
    Press Ctrl+C to exit.
    """
    if not OPENAI_API_KEY:
        print("Error: Please set OPENAI_API_KEY in your environment (in a .env file).")
        return

    recorder = AudioRecorder()
    print("Voice agent ready. Press Ctrl+C to quit.")

    try:
        while True:
            input("Press Enter to start recording...")
            
            tries = 0
            max_tries = 3
            wav_path = None
            text = "" # Initialize text here

            while tries < max_tries:
                wav_path = recorder.record_audio()
                if wav_path:
                    print("Transcribing...")
                    try:
                        text = transcribe_audio(wav_path, OPENAI_API_KEY)
                        if text.strip(): # Check if transcript is not empty or just whitespace
                            break # Exit retry loop if valid transcript is obtained
                        else:
                            print(f"Attempt {tries + 1}/{max_tries}: Empty transcript. Retrying...")
                            os.remove(wav_path) # Remove empty audio file
                            text = "" # Ensure text is empty if transcription is empty
                    except Exception as e:
                        print(f"Attempt {tries + 1}/{max_tries}: Transcription failed: {e}. Retrying...")
                        if os.path.exists(wav_path): # Check if file exists before trying to remove
                            os.remove(wav_path) # Remove problematic audio file
                        text = "" # Ensure text is empty if transcription fails
                else:
                    print(f"Attempt {tries + 1}/{max_tries}: No audio captured. Retrying...")
                    text = "" # Ensure text is empty if no audio is captured
                tries += 1
            
            if not wav_path or not text.strip():
                print("Failed to capture or transcribe clear speech after multiple attempts.")
                continue

            print(f"🗣️ You said: {text}")
            save_transcript({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "file": wav_path,
                "text": text
            })
            print("Saved to notes/transcripts.jsonl")
            
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")

voice_agent()


