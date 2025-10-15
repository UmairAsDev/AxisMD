import asyncio
import websockets
import torch
import torchaudio
import pyaudio
import torchaudio.transforms as T
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
async def send_audio():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("Connected to WebSocket, streaming audio...")
        try:
            while True:
                audio_data = stream.read(CHUNK)
                await websocket.send(audio_data)
                await asyncio.sleep(0.01) 
        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
if __name__ == "__main__":
    asyncio.run(send_audio())