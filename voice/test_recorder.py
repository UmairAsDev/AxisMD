import unittest
from recorder import AudioRecorder
import os

class TestAudioRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = AudioRecorder()

    def test_initial_state(self):
        self.assertFalse(self.recorder.is_recording)
        self.assertEqual(self.recorder.buffer, [])
        self.assertIsNone(self.recorder.start_time)
        self.assertIsNone(self.recorder.end_time)

    def test_start_and_stop(self):
        self.recorder.start()
        self.assertTrue(self.recorder.is_recording)
        self.recorder.stop()
        self.assertFalse(self.recorder.is_recording)

    def test_save_file_no_audio(self):
        filename = "test_output.wav"
        self.recorder.save_file(filename)
        self.assertFalse(os.path.exists(filename))

    def tearDown(self):
        filename = "test_output.wav"
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    unittest.main()
