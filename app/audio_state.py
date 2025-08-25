import io
import os
import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from langgraph.graph import MessagesState
from openai import OpenAI



_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def record_audio_until_stop(state: MessagesState):

    """Records audio from the microphone until Enter is pressed, then saves it to a .wav file."""
    
    audio_data = [] 
    recording = True 
    sample_rate = 16000 

    def record_audio():
        """Continuously records audio until the recording flag is set to False."""
        nonlocal audio_data, recording
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            print("Recording your instruction! ... Press Enter to stop recording.")
            while recording:
                audio_chunk, _ = stream.read(1024)  
                audio_data.append(audio_chunk)
    
        
    def stop_recording():
        """Waits for user input to stop the recording."""
        input() 
        nonlocal recording
        recording = False


    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()


    stop_thread = threading.Thread(target=stop_recording)
    stop_thread.start()


    stop_thread.join()
    recording_thread.join()


    audio_data = np.concatenate(audio_data, axis=0)
    
    audio_bytes = io.BytesIO()
    write(audio_bytes, sample_rate, audio_data)
    audio_bytes.seek(0)  
    audio_bytes.name = "audio.wav" 

    # Transcribe via Whisper
    transcription = _openai_client.audio.transcriptions.create(
       model="gpt-4o-mini-transcribe", 
       file=audio_bytes,
    )

    print("Here is the transcription:", transcription.text)