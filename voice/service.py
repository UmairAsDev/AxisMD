# from voice.recorder import AudioRecorder
# from voice.prompt_template import ClinicalPromptBuilder
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class SpeechService:
    def __init__(self):
        # self.recorder = AudioRecorder()
        pass
    
    def speech_to_text(self):
       client = OpenAI()
       audio_file = open("voice/my_recording.wav","rb")
       transcription = client.audio.transcriptions.create(
           model = "gpt-4o-mini-transcribe",
           file = audio_file,
           response_format="json",
           language = "en",
           prompt = """While converting an audio file to text you have to make sure to
            follow the following instructions:
            Instructions:
            - The speech includes the doctor(it could be any type of doctor) speaking about the details about the patient.
            - Make sure to remove the background noise if any.
            - Model should capture the all content clearly and accurately, even if the speech frequency is low.
            - If you don't understand any word in audio file clearly then guess the word based on the sentiment and what is the user(doctor) trying to convey.
            - Make sure all segemnts of speech are connected while transcribing, because there may be silence gaps between it.
            - If there is no clear speech detected within the audio file then generate error, "Error: Could not detect any speech in audio file. Please try again."
            """
       )
       return transcription.text
    

if __name__ == "__main__":
    llm_resonse = SpeechService()
    print(f"Text: {llm_resonse.speech_to_text()}")