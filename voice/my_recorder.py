import sounddevice as sd
from scipy.io.wavfile import write


class AudioRecorder():
    def __init__(self, sample_rate=44100, seconds=5, channels=1):
        self.sample_rate = sample_rate  # Sample rate
        self.seconds = seconds  # Duration of recording
        self.channels = channels

    def record_audio(self):
        print("start speaking...")
        myrecording = sd.rec(int(self.sample_rate * self.seconds), samplerate=self.sample_rate, channels=2)
        sd.wait()  # Wait until recording is finished
        my_audio = write('output.wav', self.sample_rate, myrecording)  # Save as WAV file
        return my_audio