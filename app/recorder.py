import os
import time
import wave
import threading
import pyaudio
import webrtcvad
from openai import OpenAI
from langchain_core.messages import HumanMessage



def audio_processor(sample_rate=16000, frame_duration=30):
    frame_size = int(sample_rate * frame_duration / 1000)
    vad = webrtcvad.Vad(3)
    channels = 1
    fmt = pyaudio.paInt16
    buffer = []
    is_recording = False
    start_time = None
    end_time = None

    def start():
        nonlocal is_recording, buffer, start_time, end_time
        is_recording = True
        buffer = []
        start_time = time.time()

        def record_loop():
            pa = pyaudio.PyAudio()
            stream = pa.open(format=fmt,
                             channels=channels,
                             rate=sample_rate,
                             input=True,
                             frames_per_buffer=frame_size)

            while is_recording:
                pcm = stream.read(frame_size, exception_on_overflow=False)
                if vad.is_speech(pcm, sample_rate):
                    buffer.append(pcm)

            end_time = time.time()
            stream.stop_stream()
            stream.close()
            pa.terminate()

        threading.Thread(target=record_loop, daemon=True).start()
        print("Recording started...")

    def stop():
        nonlocal is_recording
        is_recording = False
        print("Recording stopped.")

    def save_file(filename="speech.wav"):
        if buffer:
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(fmt))
                wf.setframerate(sample_rate)
                wf.writeframes(b"".join(buffer))
            print(f"Saved audio to {filename}")
            return filename
        else:
            print("No speech detected")
            return None

    def get_conversation_time():
        if start_time and end_time:
            return round(end_time - start_time, 2)
        return 0

    return {
        "start": start,
        "stop": stop,
        "save_file": save_file,
        "get_conversation_time": get_conversation_time,
    }


