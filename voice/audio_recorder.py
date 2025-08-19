import os
import sys
import threading
import queue
from time import monotonic
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment, silence as pydub_silence

try:
    from pydub import AudioSegment, silence as pydub_silence
    _PYDUB_AVAILABLE = True
except Exception:
    _PYDUB_AVAILABLE = False


class AudioRecorder:
    """
    Robust audio recorder with adaptive silence detection + post-processing.
    - Records until manual stop (Enter) or trailing silence.
    - Keeps all speech bursts in one clip.
    - Trims long leading/trailing silence and collapses internal gaps.
    - Returns a clean WAV file path or None if nothing usable.
    """

    def __init__(
        self,
        samplerate: int = 16000,
        channels: int = 1,
        dtype: str = "float32",
        out_dir: str = "audio",
        calibration_seconds: float = 0.6,
        frame_ms: int = 20,
        min_speech_ms: int = 400,
        start_grace_ms: int = 500,
        silence_duration_ms: int = 1200,
        vad_sensitivity: float = 3.0,
        hard_min_rms: float = 0.005,
        max_seconds: int = 60,
        # Post-processing
        min_silence_len: int = 800,   # ms of silence to split segments
        silence_thresh_db: int = -20, # dB below which is silence
        keep_silence: int = 200       # ms padding kept around segments
    ):
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

        self.calibration_seconds = calibration_seconds
        self.frame_ms = frame_ms
        self.min_speech_ms = min_speech_ms
        self.start_grace_ms = start_grace_ms
        self.silence_duration_ms = silence_duration_ms
        self.vad_sensitivity = vad_sensitivity
        self.hard_min_rms = hard_min_rms
        self.max_seconds = max_seconds

        self.min_silence_len = min_silence_len
        self.silence_thresh_db = silence_thresh_db
        self.keep_silence = keep_silence

    # ----------------------- Utils -----------------------

    def _rms(self, x: np.ndarray) -> float:
        if x.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(x.astype("float32")))))

    def _calibrate_noise(self) -> float:
        frames = int(self.samplerate * self.calibration_seconds)
        if frames <= 0:
            return 0.0
        try:
            data = sd.rec(frames, samplerate=self.samplerate, channels=self.channels, dtype=self.dtype)
            sd.wait()
            return self._rms(data)
        except Exception as e:
            print(f"Calibration failed: {e}", file=sys.stderr)
            return 0.0

    def _make_filename(self) -> str:
        base = os.path.join(self.out_dir, "audio_input.wav")
        if not os.path.exists(base):
            return base
        stem, ext = os.path.splitext(base)
        i = 1
        while True:
            cand = f"{stem}_{i}{ext}"
            if not os.path.exists(cand):
                return cand
            i += 1

    # ----------------------- Recording -----------------------

    def record_audio(self) -> Optional[str]:
        print("Calibrating ambient noise... stay quiet.")
        noise_rms = self._calibrate_noise()
        speech_threshold = max(self.hard_min_rms, noise_rms * self.vad_sensitivity)
        print(f"Noise floor≈{noise_rms:.4f}, threshold≈{speech_threshold:.4f}")

        q: queue.Queue[np.ndarray] = queue.Queue()
        frames = []
        speech_ms = 0
        last_voice_time = None
        start_time = monotonic()
        grace_until = start_time + (self.start_grace_ms / 1000.0)
        stop_flag = {"stop": False}

        def _on_input():
            try:
                input()  # Enter to stop manually
                stop_flag["stop"] = True
            except EOFError:
                pass

        threading.Thread(target=_on_input, daemon=True).start()

        def callback(indata, frames_count, time_info, status):
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        chunk = int(self.samplerate * (self.frame_ms / 1000.0))

        with sd.InputStream(samplerate=self.samplerate, channels=self.channels,
                            dtype=self.dtype, callback=callback):
            print("Recording... Speak naturally. Press Enter to stop.")
            while True:
                now = monotonic()
                if stop_flag["stop"] or (now - start_time) >= self.max_seconds:
                    break
                try:
                    data = q.get(timeout=0.2)
                except queue.Empty:
                    continue

                frames.append(data)

                rms = self._rms(data)
                is_voiced = rms >= speech_threshold
                if is_voiced:
                    last_voice_time = now
                    speech_ms += self.frame_ms

                if now >= grace_until and speech_ms >= self.min_speech_ms:
                    if not is_voiced and last_voice_time:
                        silence_ms = (now - last_voice_time) * 1000.0
                        if silence_ms >= self.silence_duration_ms:
                            print("Auto-stopped on trailing silence.")
                            break

        if not frames:
            print("No audio captured.")
            return None

        audio = np.concatenate(frames, axis=0).astype("float32")
        wav_path = self._make_filename()
        sf.write(wav_path, (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16),
                 self.samplerate, subtype="PCM_16")

        # ----------------------- Post-process -----------------------
        if not _PYDUB_AVAILABLE:
            print("Saved raw audio (pydub not available):", wav_path)
            return wav_path

        seg = AudioSegment.from_wav(wav_path)
        chunks = pydub_silence.split_on_silence(
            seg,
            min_silence_len=self.min_silence_len,
            silence_thresh=self.silence_thresh_db,
            keep_silence=self.keep_silence
        )

        if not chunks:
            print("No valid speech detected.")
            os.remove(wav_path)
            return None

        # Concatenate chunks with short gaps
        combined = AudioSegment.silent(duration=0)
        gap = AudioSegment.silent(duration=self.keep_silence)
        for c in chunks:
            combined += c + gap

        # Save cleaned version
        sf.write(wav_path, np.array(combined.get_array_of_samples()).astype(np.int16),
                 combined.frame_rate, subtype="PCM_16")
        print(f"Saved cleaned speech audio: {wav_path}")
        return wav_path
