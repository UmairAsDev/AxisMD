import pyaudio
import wave
import webrtcvad
import threading
import time

class AudioRecorder:
    def __init__(self, sample_rate=16000, frame_duration=30):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(3)
        self.channels = 1
        self.format = pyaudio.paInt16
        self.buffer = []
        self.is_recording = False
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start recording until stopped manually."""
        self.is_recording = True
        self.buffer = []
        self.start_time = time.time()

        def record_loop():
            pa = pyaudio.PyAudio()
            stream = pa.open(format=self.format,
                             channels=self.channels,
                             rate=self.sample_rate,
                             input=True,
                             frames_per_buffer=self.frame_size)

            while self.is_recording:
                pcm = stream.read(self.frame_size, exception_on_overflow=False)
                if self.vad.is_speech(pcm, self.sample_rate):
                    self.buffer.append(pcm)

            self.end_time = time.time()
            stream.stop_stream()
            stream.close()
            pa.terminate()


        threading.Thread(target=record_loop, daemon=True).start()
        print("Recording started...")

    def stop(self):
        """Stop recording."""
        self.is_recording = False
        print("Recording stopped.")

    def save_file(self, filename="speech.wav"):
        if self.buffer:
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b"".join(self.buffer))
            print(f"Saved audio to {filename}")
        else:
            print("No speech detected")

    def get_conversation_time(self):
        """Get total recording time."""
        if self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 2)
        return 0


if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.start()
    print("Recording for 50 seconds...")
    time.sleep(50)
    recorder.stop()
    recorder.save_file("my_recording.wav")
    print("Done! Saved as my_recording.wav")
