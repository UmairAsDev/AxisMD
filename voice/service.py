
from voice.recorder import AudioRecorder
from voice.prompt_template import ClinicalPromptBuilder

class SpeechService:
    def __init__(self):
        self.recorder = AudioRecorder()
    
    def speech_to_text(self):
       pass