"""
voice_input.py — listens on the USB microphone and turns speech into text,
and speaks text back out.

Two STT backends are supported:
  * Google's free web API via `speech_recognition` (needs internet, zero setup)
  * Vosk, fully offline (needs a downloaded model — see README)
Pick the one that suits how you want this robot to run.

TTS is done via espeak-ng (offline, no API key, works with no network at all —
matching Coglet's "works offline" design goal).
"""

import subprocess
import speech_recognition as sr

import config


def speak(text: str, voice_speed_wpm: int = 165):
    """Offline TTS via espeak-ng. Install with: sudo apt install espeak-ng"""
    subprocess.run(["espeak-ng", "-s", str(voice_speed_wpm), text])


class Listener:
    def __init__(self, use_offline_vosk: bool = False, vosk_model_path: str = None):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.use_offline = use_offline_vosk
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        if self.use_offline:
            from vosk import Model, KaldiRecognizer
            import json
            self._json = json
            self._vosk_model = Model(vosk_model_path)

    def listen_once(self) -> str:
        """Blocks until a phrase is captured, returns recognized text (or '')."""
        with self.mic as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=config.LISTEN_TIMEOUT_S,
                    phrase_time_limit=config.PHRASE_TIME_LIMIT_S,
                )
            except sr.WaitTimeoutError:
                return ""

        if self.use_offline:
            rec = self._vosk_KaldiRecognizer_new(audio)
            return rec

        try:
            return self.recognizer.recognize_google(audio)
        except (sr.UnknownValueError, sr.RequestError):
            return ""

    def _vosk_KaldiRecognizer_new(self, audio):
        from vosk import KaldiRecognizer
        rec = KaldiRecognizer(self._vosk_model, 16000)
        rec.AcceptWaveform(audio.get_raw_data(convert_rate=16000, convert_width=2))
        result = self._json.loads(rec.Result())
        return result.get("text", "")


if __name__ == "__main__":
    speak("Hello, I am listening.")
    listener = Listener()
    print("Say something...")
    print("Heard:", listener.listen_once())
