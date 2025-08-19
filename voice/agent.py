
import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
from datetime import datetime
from audio_recorder import AudioRecorder
from stt import transcribe_audio
from notes import save_transcript

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
            wav_path = recorder.record_audio()
            if not wav_path:
                print("No audio captured.")
                continue

            print("Transcribing...")
            try:
                # transcribe_audio is sync; keep call simple.
                text = transcribe_audio(wav_path, OPENAI_API_KEY)
            except Exception as e:
                print(f"Transcription failed: {e}")
                continue

            if text:
                print(f"🗣️ You said: {text}")
                save_transcript({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "file": wav_path,
                    "text": text
                })
                print("Saved to notes/transcripts.jsonl")
            else:
                print("Empty transcript.")
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")

voice_agent()